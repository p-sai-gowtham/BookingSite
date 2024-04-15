# Generated by Django 5.0.2 on 2024-02-13 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="car_drop_off_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="car",
            name="car_drop_off_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="car",
            name="car_pick_up_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="car",
            name="car_pick_up_time",
            field=models.TimeField(blank=True, null=True),
        ),
    ]
