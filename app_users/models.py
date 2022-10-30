from db_file_storage.model_utils import delete_file, delete_file_if_needed

from site_settings.tools import PhoneValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserCustomManager(models.QuerySet):
    def get_users_contacts_by_organization(self, org_id):
        queryset = self.filter(organization__id=org_id) \
            .values("first_name", "email", "photo", "phone_number", "organization__id")
        return queryset


class User(AbstractUser):
    phone_validator = PhoneValidator.get_phone_validator()
    # photo = models.ImageField(upload_to='users_photo/', default='', blank=True)
    phone_number = models.CharField(validators=phone_validator, max_length=16, unique=False,  blank=True)
    reservation_without_payment = models.BooleanField(default=False, blank=False)

    # objects = UserCustomManager.as_manager()
    photo = models.ImageField(
            upload_to=r"app_users.UserMediaDBStorage/bytes/filename/mimetype",
            blank=True,
            null=True,
       )

    def save(self, *args, **kwargs):
        delete_file_if_needed(self, 'photo')
        super(User, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(User, self).delete(*args, **kwargs)
        delete_file(self, 'photo')

    # @property
    def organization_admin(self, organization_id):
        qs = User.objects.prefetch_related("organization").filter(organization__id=organization_id, pk=self.id)
        return qs.exists()


class UserMediaDBStorage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)