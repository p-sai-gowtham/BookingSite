from django.urls import path
from . import views
from car_reservation.views import PaymentSuccessful, checking_before_payment, PaymentFailed

app_name = "attractions"  # here I gave a name for the app in order not to mix between views later when using them in other apps, so it's gonna be used like this 'appName:viewName' --example--> 'accounts:login'


urlpatterns = [
    path("", views.home, name='categories'),
    path("activities/<str:category>/", views.activities, name='activities'),
    path('activities/reserving/payment-success/<int:id>/<str:the_date>/<int:tickets_nb>/', PaymentSuccessful, name='payment-success'),
    path('activities/reserving/car_reservation/car_reserve/payment-failed/<int:id>/<str:the_date>/<int:tickets_nb>/', PaymentFailed, name='payment-failed'),
    path('activities/<str:category>/activity_reserve/paypalmiddle/<int:id>/<str:model_name>/', checking_before_payment, name="checking_before_payment")
]
