# Generated by Django 5.0.2 on 2024-03-11 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0042_car_pending"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="invoice",
            name="created_on",
        ),
    ]
