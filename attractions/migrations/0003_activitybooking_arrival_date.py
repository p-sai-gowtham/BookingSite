# Generated by Django 5.0.2 on 2024-03-30 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attractions", "0002_remove_activity_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="activitybooking",
            name="arrival_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
