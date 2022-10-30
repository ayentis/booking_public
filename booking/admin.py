from django.contrib import admin
from booking.models import Organization, OrganizationMedia, OrganizationDescription
from booking.models import ApartmentPrice, Apartment
from booking.models import ReservationMatrix, Order
from booking.models import OrganizationMediaDBStorage

from db_file_storage.form_widgets import DBAdminClearableFileInput
from django import forms


class OrganizationDescriptionInline(admin.TabularInline):
    model = OrganizationDescription
    max_num = 3


class ReservationMatrixInline(admin.TabularInline):
    model = ReservationMatrix
    extra = 0
    can_delete = False
    readonly_fields = ("apartment", "data")


class OrganizationAdmin(admin.ModelAdmin):

    list_display = ("name",)
    inlines = [OrganizationDescriptionInline]


class OrganizationDescriptionAdmin(admin.ModelAdmin):

    list_display = (
        "organization",
        "language",
    )


class ApartmentAdmin(admin.ModelAdmin):
    list_filter = ("name", "organization")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("date_time","apartment", "status", "price", "id")
    inlines = [ReservationMatrixInline]


class ApartmentPriceAdmin(admin.ModelAdmin):
    list_filter = ["category", "organization"]


# class ReservationMatrixAdmin(admin.ModelAdmin):
#     list_filter = ('name', 'organization')


class OrganizationMediaDBStorageForm(forms.ModelForm):
    class Meta:
        model = OrganizationMediaDBStorage
        exclude = []
        widgets = {
            'picture': DBAdminClearableFileInput
        }


class OrganizationMediaDBStorageAdmin(admin.ModelAdmin):
    form = OrganizationMediaDBStorageForm
    list_display = ("filename", "mimetype")


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationMedia)
admin.site.register(OrganizationDescription, OrganizationDescriptionAdmin)
admin.site.register(ApartmentPrice, ApartmentPriceAdmin)
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(ReservationMatrix)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrganizationMediaDBStorage, OrganizationMediaDBStorageAdmin)
