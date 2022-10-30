# Generated by Django 4.0.4 on 2022-06-16 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(default='', upload_to='users_photo/'),
        ),
    ]
