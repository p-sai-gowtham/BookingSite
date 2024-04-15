import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'girls_project.settings')
django.setup()

from attractions.models import Activity


csv_file = "paris_data.csv"


def populate_database_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Create Activity object
            activity = Activity.objects.create(
                name=row['name'],
                title=row['title'],
                description=row['description'],
                pricea=row['pricea'],
                category=row['category'],
                city=row['city']
            )
            # Save the Activity object
            activity.save()


populate_database_from_csv(csv_file)
