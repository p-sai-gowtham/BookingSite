import csv
from datetime import datetime
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'girls_project.settings')
django.setup()

from attractions.models import Activity, Tickets


csv_file = "paris_tickets.csv"


def populate_tickets_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            activity_name = row['activity_name']
            activity = Activity.objects.get(name=activity_name)

            date_str = row['date']
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            ticket = Tickets.objects.create(
                activity_id=activity,
                date=date,
                nba=row['nba']
            )
            ticket.save()


populate_tickets_from_csv(csv_file)
