# Generated by Django 5.0.2 on 2024-03-08 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("car_reservation", "0027_rename_id_invoice_invoice_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="invoice_id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
