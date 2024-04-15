from django.shortcuts import render, redirect  # to render an html page or redirect to a view
from django.contrib.auth import authenticate, login, logout  # functions to use
from django.contrib import messages  # for error message to the user (when he inputs a username that already exists, a weak password, or wrong username/password when logging-in)
from .forms import RegisterationFrom, SignInForm  # my own edited version of forms (I added some feilds, and styled them for the front-end layout)
from urllib.parse import urlparse, urlunparse  # to parse the url
from django.core.mail import send_mail  # the function to send an email
from django.conf import settings  # to get some configuration constants from the settings
from django.template.loader import render_to_string  # to render the html email template to a string
from car_reservation.models import Carbooking, Car
from datetime import date, timedelta

# todo : add sessions (not that important really)


def login_user(request):
    if request.user.is_anonymous:  # only if the user is anonymous, otherwise redirect him to home (because he's already logged-in - not anonymous -)
        context = {}
        if request.method == 'POST':
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

            if user is not None:
                login(request, user)
                if 'next' in request.POST:  # here I did this to redirect from the page where from he was redirected to authentify (for example: he clicks the 'book now' button then if he's not logged-in he's gonna be redirected to log-in(or sign-up), then when he's authentified he'll gonna be redirected to continue booking)
                    # just some parsing
                    next_url = request.POST['next']
                    base_url = urlparse(request.build_absolute_uri())
                    full_url = urlunparse((base_url.scheme, base_url.netloc, next_url, '', '', ''))

                    return redirect(full_url)
                else:
                    return redirect("home")
            else:
                # if he inputs a wrong username/password
                messages.info(request, "Username or Password wrong !")

        form = SignInForm()  # to render the sign-in form
        context['form'] = form
        return render(request, "login.html", context)
    else:
        return redirect("home")  # if he's not anonymous (already logged-in)


def logout_user(request):
    if request.user.is_anonymous is not True:  # he has to be logged-in to log-out
        logout(request)
    return redirect("home")


def register_user(request):
    if request.user.is_anonymous:
        context = {}
        if request.method == 'POST':
            form = RegisterationFrom(request.POST)  # to pass the user's input(to check it)

            if form.is_valid():  # if it's valid
                form.save()  # save it
                # arguments for building the message to the send (like context)
                msg_args = {'first_name': request.POST['first_name'], 'last_name': request.POST['last_name'], 'username': request.POST['username']}
                msg_plain = render_to_string('email_text.txt', msg_args)  # the plain text message to send in order the html template failed to send
                msg_html = render_to_string('email_template.html', msg_args)  # the html template to send
                # sending the welcome email
                send_mail(f"Welcome to WanderLust, {request.POST['first_name']}!",
                          msg_plain,
                          settings.EMAIL_HOST_USER,
                          [f"{request.POST['email']}"],
                          html_message=msg_html,
                          fail_silently=False,)

                if 'next' in request.POST:
                    next_url = request.POST['next']
                    base_url = urlparse(request.build_absolute_uri())
                    full_url = urlunparse((base_url.scheme, base_url.netloc, next_url, '', '', ''))
                    return redirect(full_url)
                else:
                    return redirect("home")
            else:
                # all kinds of possible error message for the user
                messages.info(request, "Username already exists, Wrong Username form, or Weak password !")  # todo : better distinglishing between the type of error here
                if request.POST['password1'] != request.POST['password2']:
                    messages.info(request, "Wrong confirmation password !")
        else:
            form = RegisterationFrom(request.POST)
        context['form'] = form
        return render(request, "register.html", context)
    else:
        return redirect("home")


def user_account(request):
    if request.user.is_anonymous is False:
        context = {}
        invoices = Carbooking.objects.filter(user_id=request.user.id).order_by("booking_date")
        context["invoices"] = invoices
        return render(request, 'account.html', context)
    else:
        return redirect("accounts:login")


def cancel_car_booking(request, invoice_id):
    if request.user.is_anonymous is False:
        invoice = Carbooking.objects.get(booking_id=invoice_id)
        car = Car.objects.get(car_id=invoice.car_id.car_id)
        # just some checking
        if invoice.canceled is False and car.booked is True and car.pending is False:
            invoice.canceled = True
            if invoice.car_id.car_pick_up_date == invoice.pick_up_date and invoice.car_id.car_drop_off_date == invoice.drop_off_date and invoice.car_id.car_pick_up_time == invoice.pick_up_time and invoice.car_id.car_drop_off_time == invoice.drop_off_time:
                car.booked = False
                car.car_pick_up_date = date.today() + timedelta(-10)
                car.car_drop_off_date = date.today() + timedelta(-5)
                car.save()
            invoice.save()
            return redirect("accounts:account")
        else:
            return render(request, 'page404.html')
    else:
        return redirect("accounts:login")
