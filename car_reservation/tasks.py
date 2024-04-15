from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings  # to get some configuration constants from the settings
from datetime import date, timedelta, datetime, time
from .models import Carbooking
from django.db.models import Q


# to send an email before on day of the drop-off day
@shared_task
def send_drop_off_notification_task():
    # here I did something a bit creative: I'm sending the email at the same hour of the day of the pick-up-time of the car that the user chose (cuz if he chose that hour of the day to pick-up the car --> he's proly free at that hour of the day ._. )
    if int(datetime.now().strftime('%H:%M:%S')[0:2]) < 23:
        the_day_before = date.today() + timedelta(1)
        timee = time(int(datetime.now().strftime('%H:%M:%S')[0:2]) + 1, int(datetime.now().strftime('%H:%M:%S')[3:5]))
        timee2 = time(int(datetime.now().strftime('%H:%M:%S')[0:2]), int(datetime.now().strftime('%H:%M:%S')[3:5]))
        bookings = Carbooking.objects.filter(
                                            Q(drop_off_date=the_day_before)&
                                            (
                                                Q(pick_up_time__lte=timee)&
                                                Q(pick_up_time__gt=timee2)
                                            )
                                          )
    else:
        the_day_before = date.today() + timedelta(2)
        bookings = Carbooking.objects.filter(Q(drop_off_date=the_day_before))

    # sending email to all the users that have a car to drop-off tmrw
    for booking in bookings:
        user_email = booking.user_id.email
        subject = 'Car Drop-off Notification'
        email_html = render_to_string('drop_off_notification_email.html', {'invoice': booking})
        email_plain = strip_tags(email_html)
        send_mail(
            subject,
            email_plain,
            settings.EMAIL_HOST_USER,
            [user_email],
            html_message=email_html,
        )


# to send an email at the same datetime of car drop-off
@shared_task
def send_rating_notification_task():
    if int(datetime.now().strftime('%H:%M:%S')[0:2]) < 23:
        # we're in today
        timee = time(int(datetime.now().strftime('%H:%M:%S')[0:2]) + 1, int(datetime.now().strftime('%H:%M:%S')[3:5]))
        today = date.today()
    else:
        # going to the next day
        timee = time(00, int(datetime.now().strftime('%H:%M:%S')[3:5]))
        today = date.today() + timedelta(1)

    bookings = Carbooking.objects.filter(Q(drop_off_date=today) & Q(drop_off_time=timee))

    # sending an email to all the users that have a drop-off rn
    for booking in bookings:
        user_email = booking.user_id.email
        subject = 'Car Drop-off Confirmation, And Rating'
        email_html = render_to_string('final_drop_off_email.html', {'invoice': booking})
        email_plain = strip_tags(email_html)
        send_mail(
            subject,
            email_plain,
            settings.EMAIL_HOST_USER,
            [user_email],
            html_message=email_html,
        )
