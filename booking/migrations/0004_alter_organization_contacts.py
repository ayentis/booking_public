# Generated by Django 4.0.4 on 2022-06-16 08:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '0003_organization_contacts_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='contacts',
            field=models.ManyToManyField(related_name='organization', to=settings.AUTH_USER_MODEL),
        ),
    ]