from django.urls import path, re_path

from booking.views import *

from django.shortcuts import redirect


urlpatterns = [
    path('organization/<int:pk>/about/', OrganizationAbout.as_view(), name='organization_about'),
    path('organization/<int:pk>/reservation/', OrganizationReservation.as_view(), name='organization_reservation'),
    path('organization/<int:pk>/contacts/', OrganizationContacts.as_view(), name='organization_contacts'),
    path('organization/<int:pk>/add_apartment/', ApartmentCreate.as_view(), name='add_apartment'),
    path('organization/<int:pk>/add_price/', ApartmentPriceCreate.as_view(), name='add_price'),
    path('organization/<int:pk>/add_month/', OrganizationAddMonth.as_view(), name='add_month'),
    path('organization/<int:pk>/confirm_order/', ConfirmOrder.as_view(), name='confirm_order'),
    path('organization/<int:pk>/create_payment/<str:orders_ids>/', CreatePayment.as_view(), name='create_payment'),
    path('organization/<int:pk>/liqpay_server_callback/', ConfirmPayment.as_view(), name='confirm_payment'),
    path('organization/', OrganizationView.as_view(), name='organizations_main'),

    re_path(r"^$", lambda req: redirect(reverse_lazy('organizations_main'))),

]