# Generated by Django 5.0.2 on 2024-03-08 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0034_alter_booking_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="id",
            new_name="booking",
        ),
    ]
