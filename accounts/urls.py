from django.urls import path
from . import views

app_name = "accounts"  # here I gave a name for the app in order not to mix between views later when using them in other apps, so it's gonna be used like this 'appName:viewName' --example--> 'accounts:login'

urlpatterns = [
        path('login/', views.login_user, name= 'login'),
        path('logout/', views.logout_user, name= 'logout'),
        path('account/', views.user_account, name= 'account'),
        path('register/', views.register_user, name= 'register'),
        path('cancel/<int:invoice_id>/', views.cancel_car_booking , name= 'cancel_car_booking')
]
