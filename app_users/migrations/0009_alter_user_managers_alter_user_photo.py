# Generated by Django 4.0.4 on 2022-07-13 13:48

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0008_usermediadbstorage_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='app_users.UserMediaDBStorage/bytes/filename/mimetype'),
        ),
    ]
