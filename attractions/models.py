from django.db import models
# from django.contrib.auth.models import User
from userauths.models import User

# from django.utils.http import formatdate
from star_ratings.models import Rating


class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    ratinga = Rating()
    pricea = models.FloatField(max_length=10)
    category = models.CharField(max_length=20, null=True)


class Tickets(models.Model):
    # here also name changed
    activity_id = models.ForeignKey(Activity, on_delete=models.DO_NOTHING)
    date = models.DateField()
    nba = models.IntegerField()


class Activitybooking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # I did change the name here
    activity_id = models.ForeignKey(Activity, on_delete=models.DO_NOTHING, blank=False)
    booking_date = models.DateTimeField(auto_now_add=True)
    # added this
    arrival_date = models.DateField(null=True, blank=True)
    canceled = models.BooleanField(default=False)
    tickets_nb = models.IntegerField()
