from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, View, TemplateView
from django.views.generic.edit import CreateView, FormView, BaseUpdateView
from django.views.generic.base import RedirectView
from booking.models import Organization, OrganizationMedia
from booking.models import ReservationMatrix
from booking.models import ApartmentPrice
from booking.models import Order

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from liqpay.liqpay3 import LiqPay
from app_users.models import User
from booking.forms import ApartmentPriceForm, ApartmentForm, PhoneForm
from django.urls import reverse_lazy
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from os import environ

import json
import logging


logger = logging.getLogger('booking_console')


class OrganizationView(ListView):
    model = Organization
    template_name = "booking/organization.html"
    paginate_by = 10
    context_object_name = "organizations"

    def get_queryset(self):
        qs = self.model.objects.get_organization_detail_qs(self.request.LANGUAGE_CODE)
        return qs.annotate(media=Max("organizationmedia__media"))


class OrganizationAbout(DetailView):
    model = Organization
    template_name = "booking/organization_about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            pk = self.kwargs[self.pk_url_kwarg]
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = context["object"]

            context["media_list"] = OrganizationMedia.objects.filter(organization=pk)

        return context

    def get_queryset(self):
        qs = self.model.objects.get_organization_detail_qs(self.request.LANGUAGE_CODE)
        return qs


class OrganizationContacts(ListView):
    model = User
    template_name = "booking/organization_contacts.html"

    def get_queryset(self):
        # return self.model.objects.get_users_contacts_by_organization(self.kwargs["pk"])

        queryset = self.model.objects.filter(organization__id=self.kwargs["pk"]).values(
            "first_name", "email", "photo", "phone_number", "organization__id"
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization_id"] = self.kwargs["pk"]
        return context


class OrganizationReservation(ListView):
    model = ReservationMatrix
    template_name = "booking/organization_reservation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization_id"] = self.kwargs["pk"]
        context["data_structure"] = self.model.prepare_data_structure(
            context["reservationmatrix_list"]
        )
        return context

    def get_queryset(self):
        qs = self.model.objects.get_reservation_matrix(self.kwargs["pk"])
        return qs


class OrganizationAddMonth(RedirectView):
    pattern_name = "organization_reservation"

    def get_redirect_url(self, *args, **kwargs):
        org = get_object_or_404(Organization, pk=self.kwargs["pk"])
        ReservationMatrix.generate_next_organization_month(org)
        return super().get_redirect_url(*args, **kwargs)


class LocalCreateView(CreateView):
    def post(self, request, *args, **kwargs):
        url_params = {"pk": kwargs["pk"]}
        if "save_and_add_next" in request.POST:
            self.success_url = self.request.path
        elif "save" in request.POST:
            self.success_url = reverse_lazy(
                "organization_reservation", kwargs=url_params
            )
        else:
            return HttpResponseRedirect(
                reverse_lazy("organization_reservation", kwargs=url_params)
            )
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.extra_context["organization_id"] = self.kwargs["pk"]
        org = get_object_or_404(Organization, pk=self.kwargs["pk"])
        self.initial = {
            "organization": org,
        }
        context = super().get_context_data(**kwargs)
        return context


class ApartmentCreate(LoginRequiredMixin, UserPassesTestMixin, LocalCreateView):
    template_name = "booking/create.html"
    form_class = ApartmentForm
    login_url = reverse_lazy("account_login")
    extra_context = {"object_name": "Apartment"}
    # success_url = reverse_lazy("organizations_main")

    def test_func(self):
        return self.request.user.organization_admin(self.kwargs["pk"])


class ApartmentPriceCreate(LoginRequiredMixin, UserPassesTestMixin, LocalCreateView):
    template_name = "booking/create.html"
    form_class = ApartmentPriceForm
    login_url = reverse_lazy("account_login")
    extra_context = {"object_name": "Price"}

    # def get_context_data(self, **kwargs):
    #     org = get_object_or_404(Organization, pk=self.kwargs["pk"])
    #     self.initial["actual_data"] = datetime.now(),
    #         "organization": org,
    #         "actual_data": datetime.now(),
    #     }
    #
    #     if self.request.method == "POST":
    #         self.success_url = reverse_lazy("organizations_about", self.kwargs["pk"])
    #     context = super().get_context_data(**kwargs)
    #     return context

    def test_func(self):
        return self.request.user.organization_admin(self.kwargs["pk"])


class ConfirmOrder(FormView):
    template_name = "booking/ordering.html"
    form_class = PhoneForm

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        self.extra_context = kwargs
        if form.is_valid():
            booking_details_with_totals = request.session.get(
                "booking_details_with_totals"
            )
            assert booking_details_with_totals, "Booking details is empty"
            # del request.session["booking_details_with_totals"]
            new_orders = Order.save_user_data(
                json.loads(booking_details_with_totals),
                user=request.user,
                phone_number=form.cleaned_data["phone"],
            )

            return HttpResponseRedirect(
                reverse_lazy(
                    "create_payment",
                    kwargs={
                        "pk": kwargs["pk"],
                        "orders_ids": Order.build_orders_id_as_str(new_orders),
                    },
                )
            )

        if booking_result := request.POST.get("booking_result"):

            booking_details = ApartmentPrice.objects.get_apartment_price_on_date(
                json.loads(booking_result)
            )
            request.session["booking_details_with_totals"] = json.dumps(
                Order.get_data_with_totals(booking_details), default=str
            )
        #     TODO: decide set initial admin phone number or not
        # form.phone = request.user.phone_number if request.user.is_authenticated else ""

        self.extra_context["booking_details_with_totals"] = json.loads(
            request.session.get("booking_details_with_totals", {})
        )
        self.extra_context["form"] = form
        self.extra_context[
            "TIMEOUT_AWAIT_ON_HOLD_ORDER"
        ] = settings.TIMEOUT_AWAIT_ON_HOLD_ORDER

        context = self.get_context_data()

        return self.render_to_response(context=context)


class CreatePayment(TemplateView):
    template_name = "booking/payment.html"

    def get_context_data(self, **kwargs):
        # org = get_object_or_404(Organization, pk=self.kwargs["pk"])
        # order = get_object_or_404(Order, pk=self.kwargs["pk"])
        schema = self.request.scheme
        domain = self.request.META.get("HTTP_HOST")
        redirect_path = reverse_lazy(
            "organization_reservation", kwargs={"pk": kwargs["pk"]}
        )
        server_path = reverse_lazy("confirm_payment", kwargs={"pk": kwargs["pk"]})
        self.extra_context = {
            "pk": kwargs.get("pk"),
            "result_url": f"{schema}://{domain}{redirect_path}",
            "server_url": f"{schema}://{domain}{server_path}",
        }

        context = super().get_context_data(**kwargs)
        context["liqpay_data"] = Order.get_payments_data(context)
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ConfirmPayment(BaseUpdateView):

    def dispatch(self, request, **kwargs):
        logger.info(f"Confirm task {request.method}")
        public_key = environ.get("LIQPAY_PUBLIC_KEY")
        private_key = environ.get("LIQPAY_PRIVATE_KEY")
        liqpay = LiqPay(public_key, private_key)
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(private_key + data + private_key)
        if sign == signature:
            logger.info('callback is valid')
            response = liqpay.decode_data_from_str(data)
            orders_ids_list = Order.build_orders_id_as_list(response["order_id"])
            orders_qs = Order.get_orders_by_id_list(orders_ids_list)
            for order in orders_qs:
                order.set_status_reserved()
                logger.info(f'Reserved for order {order}')

        logger.info(f'callback data {response}')
        return HttpResponse()



