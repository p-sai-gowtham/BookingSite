"""hms_prj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps Routes
    path("hotel/", include("hotel.urls")),
    path("hotel/booking/", include("booking.urls")),
    path("hotel/user/", include("userauths.urls")),
    path("hotel/dashboard/", include("user_dashboard.urls")),

    # Ckeditor
    path("hotel/ckeditor5/", include('django_ckeditor_5.urls')),
    

    path('car/home/', include('car_reservation.urls')),
    path('car/', include('paypal.standard.ipn.urls')),
    path('car/accounts/', include('accounts.urls')),
    path('car/ratings/', include('star_ratings.urls', namespace='ratings')),
    path("car/attractions/", include("attractions.urls")),

    path('flight/',include("flight.urls")),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico')))

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

