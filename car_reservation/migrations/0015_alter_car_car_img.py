# Generated by Django 5.0.2 on 2024-02-19 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0014_alter_car_car_img"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="car_img",
            field=models.FilePathField(blank=True, null=True),
        ),
    ]
