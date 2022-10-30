# Generated by Django 4.0.4 on 2022-07-08 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0010_order_date_time_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationMediaDBStorage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bytes', models.TextField()),
                ('filename', models.CharField(max_length=255)),
                ('mimetype', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='organizationmedia',
            name='media',
            field=models.ImageField(blank=True, null=True, upload_to='booking.OrganizationMediaDBStorage/bytes/filename/mimetype'),
        ),
    ]
