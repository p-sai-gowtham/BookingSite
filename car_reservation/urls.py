from django.urls import path
from . import views


urlpatterns = [
        path('', views.home, name="home"),
        path('drop_off_confirmation/<int:id>/', views.drop_off_confirmation, name="drop_off_confirmation"),
        path('car_reservation/', views.search, name="search"),
        path('car_reservation/car_reserve/', views.reserving, name="reserving_a_car"),
        path('car_reservation/car_reserve/paypalmiddle/<int:id>/<str:model_name>/', views.checking_before_payment, name="checking_before_payment"),

        path('car_reservation/car_reserve/payment-success/<int:id>/<str:the_date>/', views.PaymentSuccessful, name='payment-success'),
        path('car_reservation/car_reserve/payment-failed/<int:id>/<str:the_date>/', views.PaymentFailed, name='payment-failed'),

]
