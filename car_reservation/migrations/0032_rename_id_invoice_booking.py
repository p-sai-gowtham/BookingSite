# Generated by Django 5.0.2 on 2024-03-08 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0031_rename_booking_invoice_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invoice",
            old_name="id",
            new_name="booking",
        ),
    ]