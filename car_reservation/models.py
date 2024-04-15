from django.db import models
# from django.contrib.auth.models import User
from userauths.models import User
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating


class Car(models.Model):
    car_id = models.IntegerField(primary_key=True)
    car_current_location = models.CharField(max_length=50)
    car_brand = models.CharField(max_length=20)
    car_model = models.CharField(max_length=50)
    car_price_perday = models.FloatField(null=True, blank=True)
    city_Mpg_For_Diesel = models.IntegerField(null=True, blank=True)
    Co2_fuel_Diesel = models.IntegerField(null=True, blank=True)
    Cylinders = models.IntegerField(null=True, blank=True)
    Drive = models.CharField(max_length=100, null=True, blank=True)
    Fuel_Type = models.CharField(max_length=20, null=True, blank=True)
    Transmission = models.CharField(max_length=50, null=True, blank=True)
    Vehicle_Size_Class = models.CharField(
        max_length=100, null=True, blank=True)
    availability = models.BooleanField(null=True, blank=True)
    Year = models.IntegerField(null=True, blank=True)
    baseModel = models.CharField(max_length=50, null=True, blank=True)
    car_pick_up_date = models.DateField(null=True, blank=True)
    car_pick_up_time = models.TimeField(null=True, blank=True)
    car_drop_off_date = models.DateField(null=True, blank=True)
    car_drop_off_time = models.TimeField(null=True, blank=True)
    car_img = models.ImageField(null=True, blank=True)
    booked = models.BooleanField(default=False)
    pending = models.BooleanField(default=False)
    ratings = GenericRelation(Rating, related_query_name='cars')
    # Car.objects.filter(ratings__isnull=False).order_by('ratings__average')


class Carbooking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    car_id = models.ForeignKey(Car, on_delete=models.DO_NOTHING, blank=False)
    booking_date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    pick_up_date = models.DateField(null=True, blank=True)
    pick_up_time = models.TimeField(null=True, blank=True)
    drop_off_date = models.DateField(null=True, blank=True)
    drop_off_time = models.TimeField(null=True, blank=True)
    canceled = models.BooleanField(default=False)
