"""site_settings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.i18n import i18n_patterns

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, re_path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from db_file_storage import views as db_file_storage_views


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("allauth.urls")),
    re_path(r"^admin/", admin.site.urls),
    # STORAGE IN DATABASE SETTINGS
    re_path(r"^files/", include("db_file_storage.urls")),
    re_path(
        r"^console-picture-view/",
        db_file_storage_views.get_file,
        {"add_attachment_headers": False, "extra_headers": {"Content-Language": "en"}},
        name="view_picture",
    ),
    re_path(
        r"^console-picture-download/",
        db_file_storage_views.get_file,
        {
            "add_attachment_headers": True,  # Shows a "File Download" box in the browser
            "extra_headers": {"Content-Language": "en"},
        },
        name="download_picture",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    re_path(r"^booking/", include("booking.urls")),
    re_path(r"^app_users/", include("app_users.urls")),
    re_path(r"^$", lambda req: redirect(reverse_lazy("organizations_main"))),
)
