# Generated by Django 5.0.2 on 2024-02-18 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0007_rename_availablality_car_availability"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="car_img",
            field=models.URLField(),
        ),
    ]