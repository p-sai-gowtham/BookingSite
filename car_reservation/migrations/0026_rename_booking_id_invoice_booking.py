# Generated by Django 5.0.2 on 2024-03-08 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0025_rename_car_booking_car_id_alter_booking_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invoice",
            old_name="booking_id",
            new_name="booking",
        ),
    ]