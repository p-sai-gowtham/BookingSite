# Generated by Django 4.2.4 on 2023-09-14 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wallet',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]