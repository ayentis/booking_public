from django.db.models import Q, Max, Subquery, OuterRef
from db_file_storage.model_utils import delete_file, delete_file_if_needed

from site_settings.tools import ApartmentBookingStatus, ApartmentCategory
from site_settings.tools import PhoneValidator

from django.utils.translation import gettext_lazy as _

from datetime import date, timedelta, datetime
from django.utils.timezone import now

from dateutil.relativedelta import relativedelta
from calendar import Calendar as Calendar_sl

from collections import OrderedDict
from collections.abc import Iterable

from django.shortcuts import get_object_or_404
from django.db import models
from django.conf import settings
from django.urls import reverse
from app_users.models import User

from django.db import IntegrityError, transaction
from site_settings.tasks import cancel_not_payed_on_hold_order
from os import environ
from liqpay.liqpay3 import LiqPay

from copy import deepcopy


class OrganizationCustomManager(models.QuerySet):
    def get_organization_detail_qs(self, language):
        qs = self.annotate(
            description=Max(
                "organizationdescription__description",
                filter=Q(organizationdescription__language=language),
            )
        ).order_by("pk")
        return qs


class ReservationMatrixCustomManager(models.QuerySet):
    def get_reservation_matrix(self, organization):
        today = date.today()

        qs = self.filter(
            data__gte=date(today.year, today.month, 1),
            apartment__organization=organization,
        ).order_by("data", "apartment__category", "apartment")

        return qs


class ApartmentPriceCustomManager(models.QuerySet):
    @staticmethod
    def _transform_input_booking_data(data):
        filter_values = {}
        for current_data in data:
            apartment_id = current_data["apartment_id"]
            if not filter_values.get(apartment_id):
                filter_values[apartment_id] = []
            filter_values[apartment_id].append(current_data["order_data"])

        return filter_values

    def get_apartment_price_on_date(self, data):

        filter_values = self._transform_input_booking_data(data)
        assert filter_values, "no one reservation"

        sq = Subquery(
            self.filter(
                category=OuterRef("apartment__category"),
                organization=OuterRef("apartment__organization"),
                actual_data__lte=OuterRef("data"),
            )
            .order_by("-actual_data")
            .values("price")[:1]
        )

        union_list = []
        for apartment_id, dates in filter_values.items():
            union_list.append(
                ReservationMatrix.objects.filter(
                    apartment_id=apartment_id, data__in=dates
                )
                .order_by()
                .annotate(price=sq)
            )

        qs = (
            union_list[0]
            if len(union_list) == 1
            else union_list[0].union(*union_list[1:])
        )

        return qs


class Organization(models.Model):
    name = models.CharField(max_length=200)
    contacts = models.ManyToManyField(User, related_name="organization")

    objects = OrganizationCustomManager.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("model-detail-view", args=[str(self.pk)])


class OrganizationMediaDBStorage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class OrganizationMedia(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    # media = models.ImageField(upload_to="organization/")
    media = models.ImageField(
        upload_to=r"booking.OrganizationMediaDBStorage/bytes/filename/mimetype",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.organization.name

    def save(self, *args, **kwargs):
        delete_file_if_needed(self, "media")
        super(OrganizationMedia, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(OrganizationMedia, self).delete(*args, **kwargs)
        delete_file(self, "media")


class OrganizationDescription(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES, max_length=10)
    description = models.TextField()

    class Meta:
        unique_together = (("organization", "language"),)

    def __str__(self):
        return self.organization.name


class Apartment(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    category = models.CharField(choices=ApartmentCategory.choices, max_length=4)

    def __str__(self):
        return f"{self.name} ({self.organization})"

    class Meta:
        verbose_name_plural = _("Apartments")
        verbose_name = _("Apartment")
        ordering = ["name"]


class ReservationMatrix(models.Model):
    data = models.DateField(blank=False, verbose_name=_("Data"))
    apartment = models.ForeignKey(Apartment, blank=False, on_delete=models.CASCADE)
    order = models.ForeignKey("Order", blank=True, null=True, on_delete=models.SET_NULL)

    objects = ReservationMatrixCustomManager.as_manager()

    class Meta:
        unique_together = (("data", "apartment"),)
        ordering = ["apartment", "data"]

    def __str__(self):
        return f"{self.apartment} ({self.data})"

    @classmethod
    def generate_next_organization_month(cls, organization: Organization) -> None:
        qs_rez = cls.objects.filter(apartment__organization=organization).aggregate(
            max_data=Max("data")
        )
        max_data = qs_rez["max_data"]
        if max_data and max_data.replace(day=1) >= date.today().replace(day=1):
            next_period = qs_rez["max_data"].replace(day=1) + relativedelta(months=1)
        else:
            next_period = date.today().replace(day=1)
        cls.generate_month_all_apartment(
            organization, next_period.month, next_period.year
        )

    @classmethod
    def generate_apartment_month(
        cls, apartment: Apartment, month: int, year=date.today().year
    ) -> None:
        calendar_obj = Calendar_sl()
        month_days_iter = calendar_obj.itermonthdays(year, month)
        objects_list = []
        for month_day in month_days_iter:
            if not month_day:
                continue
            data = date(year, month, month_day)
            objects_list.append(cls(data=data, apartment=apartment))

        try:
            cls.objects.bulk_create(objects_list)
        except Exception as e:
            print("Not created", apartment, e)

    @classmethod
    def generate_month_all_apartment(
        cls, organization: Organization, month: int, year=date.today().year
    ) -> None:
        qs = Apartment.objects.filter(organization=organization)
        for qs_apartment in qs:
            cls.generate_apartment_month(qs_apartment, month, year)

    @staticmethod
    def prepare_data_structure(
        flat_data: ReservationMatrixCustomManager,
    ) -> OrderedDict:

        structured_data = OrderedDict()

        for current_data in flat_data:

            current_month = current_data.data.strftime("%B %Y")
            current_category = current_data.apartment.get_category_display()

            if not structured_data.get(current_month):
                structured_data[current_month] = OrderedDict()

            if not structured_data[current_month].get(current_category):
                structured_data[current_month][current_category] = {
                    "column": [""],
                    "row": OrderedDict(),
                }

            working_data_dict = structured_data[current_month][current_category]
            column_list = working_data_dict["column"]
            row_dict = working_data_dict["row"]
            if not column_list or column_list[-1] != current_data.data.day:
                column_list.append(current_data.data.day)
            if not row_dict.get(current_data.apartment):
                row_dict[current_data.apartment] = []

            data_list = row_dict[current_data.apartment]
            data_list.append(
                {
                    "order": current_data.order,
                    "in_past": current_data.data < date.today(),
                    "booking_data": current_data.data,
                }
            )

        return structured_data

    @classmethod
    def save_order_data(cls, order: "Order", data: list) -> None:
        for detail in data:
            cls.objects.filter(apartment=order.apartment, data=detail[0]).update(
                order=order
            )


class Order(models.Model):
    phone_validator = PhoneValidator.get_phone_validator()
    date_time = models.DateTimeField(blank=True, auto_now_add=True)
    user = models.ForeignKey(User, null=True, on_delete=models.PROTECT, blank=True)
    phone_number = models.CharField(
        validators=phone_validator, max_length=16, unique=False, blank=True
    )
    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    status = models.CharField(
        blank=False,
        default=ApartmentBookingStatus.ON_HOLD,
        choices=ApartmentBookingStatus.choices,
        max_length=10,
    )
    comment = models.TextField(blank=True)

    @staticmethod
    def get_data_with_totals(data) -> dict:
        detail = OrderedDict()
        apartment_name = {}
        for current in data:
            # key = (current["apartment__id"], current["apartment__name"])
            key = current.apartment.id
            apartment_name[key] = current.apartment.name
            value = (current.data, current.price)
            if not detail.get(key):
                detail[key] = []
            detail[key].append(value)

        total_apartment = OrderedDict(
            {
                key: {
                    "sum": sum([elem[1] for elem in value]),
                    "name": apartment_name[key],
                }
                for key, value in detail.items()
            }
        )

        total = sum((value["sum"] for value in total_apartment.values()))
        return {"detail": detail, "total_apartment": total_apartment, "total": total}

    @classmethod
    @transaction.atomic
    def save_user_data(cls, data: dict, **kwargs) -> list:
        status = ApartmentBookingStatus.ON_HOLD
        user = kwargs.get("user")
        local_kwargs = deepcopy(kwargs)
        if user and user.is_anonymous:
            del local_kwargs["user"]
        new_orders = []
        if user and user.is_authenticated and user.reservation_without_payment:
            status = ApartmentBookingStatus.RESERVED
        for apartment, detail in data["total_apartment"].items():

            obj_order = cls.objects.create(
                apartment=get_object_or_404(Apartment, pk=int(apartment)),
                price=float(detail["sum"]),
                status=status,
                **local_kwargs,
            )
            ReservationMatrix.save_order_data(obj_order, data["detail"][apartment])

            if status == ApartmentBookingStatus.ON_HOLD:
                cancel_not_payed_on_hold_order.apply_async(
                    args=[obj_order.pk],
                    eta=now()
                    + timedelta(seconds=settings.TIMEOUT_AWAIT_ON_HOLD_ORDER * 60),
                )
            new_orders.append(obj_order)
        return new_orders

    @staticmethod
    def get_payments_data(context: dict) -> dict:

        public_key = environ.get("LIQPAY_PUBLIC_KEY")
        private_key = environ.get("LIQPAY_PRIVATE_KEY")

        liqpay = LiqPay(public_key, private_key)

        orders_ids = context.get("orders_ids")
        orders_ids_list = Order.build_orders_id_as_list(orders_ids)
        orders_qs = Order.get_orders_by_id_list(orders_ids_list)

        expired_data = now() + timedelta(seconds=settings.TIMEOUT_AWAIT_ON_HOLD_ORDER * 60)

        liqpay_data = {
            "version": "3",
            "public_key": public_key,
            # "private_key": private_key,
            "action": "pay",
            "amount": str(sum((order.price for order in orders_qs))),
            "currency": "UAH",
            "description": f"{_('Your booking orders numbers:')} {orders_ids.replace('_', ', ')}",
            "order_id": orders_ids,
            # Non obliged params
            "commission_payer": "sender",
            "result_url": context.get("result_url"),
            "expired_date": expired_data.strftime("%Y-%m-%d %H:%M:%S"),
            "sandbox": 1,  # sandbox mode, set to 1 to enable it
            "server_url": context.get("server_url"),  # url to callback view

        }
        data = liqpay.cnb_data(liqpay_data)
        signature = liqpay.cnb_signature(liqpay_data)

        liqpay_data.update(
            {
                "data": data,
                "signature": signature,
            }
        )

        return liqpay_data

    @staticmethod
    def build_orders_id_as_str(orders_ids_list: list) -> str:
        return "_".join([str(order.id) for order in orders_ids_list])

    @staticmethod
    def build_orders_id_as_list(orders_ids_str: str) -> map:
        return map(lambda x: int(x), orders_ids_str.split("_"))

    @staticmethod
    def get_orders_by_id_list(orders_ids: Iterable) -> models.QuerySet:
        return Order.objects.filter(id__in=orders_ids)

    def set_status_reserved(self) -> None:
        if self.status != ApartmentBookingStatus.RESERVED:
            self.status = ApartmentBookingStatus.RESERVED
            self.save()


class ApartmentPrice(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    actual_data = models.DateField(
        blank=False, verbose_name="Actual data", help_text="Data from price actual"
    )
    category = models.CharField(choices=ApartmentCategory.choices, max_length=4)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_category_display()} ({self.organization}) {self.actual_data}: {self.price}"

    objects = ApartmentPriceCustomManager.as_manager()
