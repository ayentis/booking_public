from django.forms import ModelForm
from django import forms
from .models import Apartment, ApartmentPrice
from site_settings.tools import PhoneValidator
from datetime import datetime


class ApartmentForm(ModelForm):
    class Meta:
        model = Apartment
        fields = ('organization', 'name', 'category')


class DateInput(forms.DateInput):
    input_type = 'date'


class ApartmentPriceForm(ModelForm):

    actual_data = forms.DateField(initial=datetime.now(), widget=DateInput)

    class Meta:
        model = ApartmentPrice
        fields = ('organization','actual_data', 'category', 'price')
        # widgets = {
        #     'actual_data': DateInput,
        # }


class PhoneForm(forms.Form):
    phone_validator = PhoneValidator.get_phone_validator()
    phone = forms.CharField(validators=phone_validator, max_length=16)

    class Meta:
        fields = ('phone',)
