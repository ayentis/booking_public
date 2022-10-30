from django.db import models
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import json


class PhoneValidator:
    @staticmethod
    def get_phone_validator():
        phone_number_regex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
        return [phone_number_regex]


class ApartmentBookingStatus(models.TextChoices):
    RESERVED = "reserved", _("Reserved")
    ON_HOLD = "on_hold", _("On hold")
    PREPARED = "prepared", _("Prepared")
    CANCELED = "canceled", _("Canceled")


class ApartmentCategory(models.TextChoices):
    ST_3 = "st_3", _("Standart 3")
    ST_4 = "st_4", _("Standart 4")


class EncodeObject(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            raise TypeError(f"{obj.__class__.__name__} is noy JSON serializable")


class DecodeOrderObject(json.JSONDecoder):
    def __init__(self):
        super(DecodeOrderObject, self).__init__(object_hook=self.decode_order)

    def decode_order(self, d):
        Order = apps.get_model(app_label="booking", model_name="Order")
        return Order(**d)
