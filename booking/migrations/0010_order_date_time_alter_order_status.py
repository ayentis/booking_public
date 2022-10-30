# Generated by Django 4.0.4 on 2022-07-01 12:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_order_comment_order_price_alter_order_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('reserved', 'Reserved'), ('on_hold', 'On hold'), ('prepared', 'Prepared'), ('canceled', 'Canceled')], default='on_hold', max_length=10),
        ),
    ]