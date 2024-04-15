from django.shortcuts import render, redirect

from .models import Car, Carbooking
from .forms import SearchCarsForm
from django.db.models import Q
from datetime import date, time, datetime, timedelta
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import urllib.parse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib import messages

from attractions.models import Activity, Activitybooking, Tickets
from attractions.forms import BookingForm


def home(request):
    context = {}
    return render(request, "home.html", context)


def is_date_valid(the_date):  # checking if the date provided by the user is valid
    length = 0
    for feild in the_date:
        length += len(feild)

    if length == 41:
        try:
            date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
            date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5]))

            time(int(the_date[1][1:3]), int(the_date[1][4:6]), int(the_date[1][7:9]))
            time(int(the_date[4][1:3]), int(the_date[4][4:6]), int(the_date[4][7:9]))
            return True
        except Exception:
            return False
    else:
        return False


def is_still_available(the_date, car):  # checking if the car is still available
    his_pick_up_date = date(int(the_date[0][6:]), int(
        the_date[0][0:2]), int(the_date[0][3:5]))

    his_pick_up_time = time(
        hour=int(the_date[1][1:3]), minute=int(the_date[1][4:6]))

    if car.car_drop_off_date < his_pick_up_date or (car.car_drop_off_date == his_pick_up_date and car.car_drop_off_time < his_pick_up_time):
        return True
    else:
        return False


# just to simplifies the code for a bit
def PayPalPayment(request, item_name, amount, paramsdict, app):  # returns a dict of arguments for PayPal payment form
    host = request.get_host()
    checkout = {
              'business': settings.PAYPAL_RECEIVER_EMAIL,  # where the money is going to (to me ofc xD)
              'amount': amount,  # the amount of money to pay
              'item_name': item_name,  # the item name (in ma case the car name
              'invoice': uuid.uuid4(),  # just a random big number for the invoice number (not id)
              'currency_code': 'USD',  # I used USD, cuz it's more convenient for travellers
              'notify_url': f"https://{host}{reverse('paypal-ipn')}",  # PayPal page to pay
              'return_url': f"https://{host}{reverse(f'{app}payment-success', kwargs=paramsdict)}",  # PayPal will redirect the user to this url if the payment went successfully (I'm passing two arguments cuz I need them to make changes in DB)
              'cancel_url': f"https://{host}{reverse(f'{app}payment-failed', kwargs=paramsdict)}",  # same thing as above just if the payment failed
            }
    return checkout


def car_booking_params(request, obj):
    context = dict()
    if 'date' in request.GET:
        the_date = request.GET.get('date').split()
        numOfDays = date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5])) - date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
        numOfDays = str(numOfDays)
        numOfDays = numOfDays.replace(':', ' ')
        numOfDays = numOfDays.split()
        numOfDays = int(numOfDays[0])
        if numOfDays == 0:
            numOfDays = 1
        else:
            numOfDays += 1

    else:
        # here the user didn't choose the his time !
        my_url = dict()
        if 'city' in request.GET:
            context["city"] = request.GET.get('city')
            my_url.update(dict({'city': request.GET.get('city')}))
        my_url.update(dict({'no_datetime': '1'}))  # this make notify him to choose a period of time
        params = my_url
        return redirect(f"http://127.0.0.1:8000/home/car_reservation/?{urllib.parse.urlencode(params)}")

    amount = (obj.car_price_perday * numOfDays)
    context["amount"] = amount
    context["numofdays"] = numOfDays
    item_name = (obj.car_brand + " " + obj.car_model)

    # if his pick-up-date is equal to the car-drop-off-date --> we adjust his pick-up-time = car-drop-off-time (cuz we tell him in the frontend that this car isn't gonna be available until the car-drop-off-time)
    if date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5])) == obj.car_drop_off_date:
        the_date = f"{the_date[0][0:2]}/{the_date[0][3:5]}/{the_date[0][6:]} ({obj.car_drop_off_time}) - {the_date[3][0:2]}/{the_date[3][3:5]}/{the_date[3][6:]} ({time(int(the_date[4][1:3]), int(the_date[4][4:6]), int(the_date[4][7:9]))})".split()

    the_date_for_url = " ".join(the_date)
    the_date_for_url = urllib.parse.quote_plus(the_date_for_url)

    paramsdict = {'id': obj.car_id, 'the_date': the_date_for_url}

    # here just treating the last case
    his_pick_up_date = date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
    his_pick_up_time = time(hour=int(the_date[1][1:3]), minute=int(the_date[1][4:6]))
    # checking if the car is ['gonna be available' or 'the car is still available']
    if obj.pending is False and ((obj.car_drop_off_date == his_pick_up_date and obj.car_drop_off_time >= his_pick_up_time) or is_still_available(the_date, obj) is True):
        # here suspend the car for some time, and then after the payment (weather success or fail --> adjust that)
        obj.pending = True
        obj.save()
    else:
        my_url = dict()
        my_url.update(dict({'city': request.GET.get('city')}))
        my_url.update(dict({'?page': request.GET.get('?page')}))
        my_url.update(dict({'date': " ".join(the_date)}))
        params = my_url
        context["Url"] = urllib.parse.urlencode(params)
        context["car"] = obj
        context["reserved"] = True  # to tell him that the car was just reserved :(
        return render(request, 'car_reserve.html', context)

    return (paramsdict, item_name, amount)


def activity_booking_params(request, attraction, category):
    booking_date = request.GET.get('booking_date')
    booking_date = date(int(booking_date[0:4]), int(booking_date[5:7]), int(booking_date[8:]))
    tickets_nb = request.GET.get('numt')
    if booking_date is None or tickets_nb is None:
        return render(request, 'page404.html')

    tickets = Tickets.objects.filter(Q(activity_id=attraction.activity_id) & Q(date=booking_date))

    # to get rid of the UnboundLocalError
    available_tickets = -1

    if len(tickets) == 1:
        for ticket in tickets:
            available_tickets = ticket.nba
        ticket = tickets[0]
    else:
        return render(request, 'page404.html')

    tickets_nb = int(tickets_nb)
    if available_tickets >= tickets_nb:
        # here we take places as if he already payed, then if he failed to pay we're gonna take 'em off
        ticket.nba = ticket.nba-int(tickets_nb)
        ticket.save()

        # params
        item_name = attraction.title
        amount = attraction.pricea * int(tickets_nb)

        paramsdict = {}
        paramsdict["id"] = attraction.activity_id
        booking_date = request.GET.get('booking_date')
        paramsdict["the_date"] = booking_date
        paramsdict["tickets_nb"] = tickets_nb

        return (paramsdict, item_name, amount)

    my_url = dict()
    my_url.update(dict({'city': attraction.city}))
    my_url.update(dict({'booking_date': request.GET.get('booking_date')}))
    my_url.update(dict({'a': ''}))
    my_url.update(dict({'numt': tickets_nb}))
    my_url.update(dict({'activity_id': attraction.activity_id}))

    params = my_url
    Urlparams = urllib.parse.urlencode(params)
    url = f"http://127.0.0.1:8000/attractions/activities/{category}/?{Urlparams}"
    # we're gonna redirect him back to the search page and tell him what's the problem (either "the tickets just run out" or "there's enough tickets for you number of tickets")
    return redirect(url)


@login_required
def checking_before_payment(request, id, model_name, category=None):  # checking if the car is still available before redirecting the user to PayPal
    context = {}
    model_mapping = {
        'Car': Car,
        'Activity': Activity,
        # 'hotels': Hotels,
        # 'flights': Flight,
    }
    model_class = model_mapping.get(model_name)
    if model_class is None:
        return render(request, 'page404.html')

    try:
        obj = model_class.objects.get(pk=id)  # here I used pk=id so in ur models the id should be set as a primary key
    except Exception:
        return render(request, 'page404.html')

    # getting the arguments for PayPalPaymentsForm

    # Note : now here cuz we didn't yet merge all our code, you'll get some
    # some error telling u that a variable is possibly unbound ---> which mean
    # that a variable is declared inside an 'if' statment and used outside it,
    # so we might not get inside that if (so that variable wouldn't exist then to use after)
    # but when we uncomment that else part of the if it'll work, and for testing just declare 
    # your variables outside the if with random values to get rid of that error then test ur code

    # look at me do it (u can keep it ot test):
    paramsdict = {}
    item_name = "whatever"
    amount = 2023234  # some random value

    if model_class == Car:  # note here u should use the class , not just the name so Car not "Car"
        carparams = car_booking_params(request, obj)
        # here I'm gonna check if the function return a tuple to get its values, otherwise it return an html page or redirected the user so we return it directly
        if isinstance(carparams, tuple):
            paramsdict = carparams[0]
            item_name = carparams[1]
            amount = carparams[2]
            # this is for testing only
            host = request.get_host()
            context["fail_path"] = f"http://{host}{reverse('payment-failed', kwargs=paramsdict)}"
            context["success_path"] = f"http://{host}{reverse('payment-success', kwargs=paramsdict)}"
            app = ''
        else:
            return carparams
    elif model_class == Activity:
        activityparams = activity_booking_params(request, obj, category)
        if isinstance(activityparams, tuple):
            paramsdict = activityparams[0]
            item_name = activityparams[1]
            amount = activityparams[2]
            # this is for testing only
            host = request.get_host()
            context["fail_path"] = f"http://{host}{reverse('attractions:payment-failed', kwargs=paramsdict)}"
            context["success_path"] = f"http://{host}{reverse('attractions:payment-success', kwargs=paramsdict)}"
            app = 'attractions:'
        else:
            return activityparams
    """
    elif model_class == Hotel:
        hotelparams = hotel_booking_params(request, obj)
        if isinstance(hotelparams, tuple):
            paramsdict = hotelparams[0]
            item_name = hotelparams[1]
            amount = hotelparams[2]
        else:
            return hotelparams
    elif model_class == Flight:
        flightparams = flight_booking_params(request, obj)
        if isinstance(flightparams, tuple):
            paramsdict = flightparams[0]
            item_name = flightparams[1]
            amount = flightparams[2]
        else:
            return flightparams
    else model_class == Activity:
        activityparams = activity_booking_params(request, obj)
        if isinstance(activityparams, tuple):
            paramsdict = activityparams[0]
            item_name = activityparams[1]
            amount = activityparams[2]
        else:
            return activityparams
    """


    # PayPalPaymentsForm
    paypal_checkout = PayPalPayment(request, item_name, amount, paramsdict, app)  # Here u must have two views named 'payment-success' and 'payment-failed' which require 2 arguments (request, id). For handling after payemnt
    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    context["paypal"] = paypal_payment

    return render(request, 'middle.html', context)


def search(request):
    context = {}
    available_cities = ["london", "uk", "maldives", "rome", "italy", "usa", "new", "york", "barcelona", "spain", "paris", "france"]
    his_pick_up_date = date.today()
    form = SearchCarsForm()
    context["form"] = form
    context["long"] = False
    if request.method == 'GET':
        context["ResultedCars"] = list()
        if len(request.GET) > 0:

            # to get the query words
            if 'city' in request.GET:
                context["city"] = request.GET.get('city')
                if 'no_datetime' in request.GET:
                    if request.GET.get('no_datetime') == '1':
                        context["no_datetime"] = True
                    else:
                        return render(request, 'page404.html', context)

                query_words = request.GET.get('city')
                query_words = query_words.lower().replace('-', ' ').split()

                # just checking if someone messed the url (provided a country that we don't provide)
                for word in query_words:
                    if not word.lower() in available_cities:
                        return render(request, 'page404.html', context)

                # just handling if the server time is 23 so 23 + 1 = 24 --but--> 23 + 1 = 00 (nxt day)
                if int(datetime.now().strftime('%H:%M:%S')[0:2]) <= 22:
                    context["the_time_today"] = time(int(datetime.now().strftime(
                        '%H:%M:%S')[0:2])+1, int(datetime.now().strftime('%H:%M:%S')[3:5]))
                    diff = 0  # keep in the currnet day
                else:
                    diff = 1  # just going to the next day -using delta- when validating datetime
                    context["the_time_today"] = time(
                        00, int(datetime.now().strftime('%H:%M:%S')[3:5]))
            else:
                return render(request, 'page404.html', context)

            if 'date' in request.GET:
                the_date = request.GET.get('date').split()
                if is_date_valid(the_date) is True:
                    form = SearchCarsForm({"date": str(request.GET.get('date'))})
                    context["form"] = form
                    his_pick_up_date = date(int(the_date[0][6:]), int(
                        the_date[0][0:2]), int(the_date[0][3:5]))

                    his_pick_up_time = time(
                        hour=int(the_date[1][1:3]), minute=int(the_date[1][4:6]))

                    # limiting the pick-up date
                    if his_pick_up_date == date.today() or his_pick_up_date <= (date.today() + timedelta(15)):
                        context["pick_up_date"] = his_pick_up_date
                        context["pick_up_time"] = his_pick_up_time
                        context["the_date_today"] = date.today()+ timedelta(diff)

                        # handling if he chooses datetime older than current datetime
                        if his_pick_up_date < date.today() or (his_pick_up_date == (date.today() + timedelta(diff)) and his_pick_up_time <= context["the_time_today"]):
                            return render(request, 'car_search.html', context)
                    else:
                        context["long"] = True
                        return render(request, 'car_search.html', context)
                else:
                    return render(request, 'page404.html', context)
            else:
                # when he comes from the home page
                his_pick_up_date = date.today() + timedelta(diff)
                his_pick_up_time = context["the_time_today"]
                context["pick_up_date"] = his_pick_up_date
                context["pick_up_time"] = his_pick_up_time

            # querying...
            selected_rating = request.GET.get('selected_rating')
            max_price = request.GET.get('max_price')
            min_price = request.GET.get('min_price')
            for word in query_words:
                # applying selected filters
                if selected_rating is not None or max_price is not None or min_price is not None:
                    if selected_rating is not None and max_price is not None and min_price is not None:
                        if int(selected_rating) < 1 or int(selected_rating) > 5:
                            return render(request, 'page404.html', context)
                        context['selected_rating'] = selected_rating
                        context['max_price'] = max_price
                        context['min_price'] = min_price
                        context["ResultedCars"] += Car.objects.filter(Q(pending=False)&
                                                                      (((Q(car_price_perday__gte=min_price) & Q(car_price_perday__lte=max_price)) &
                                                                        (Q(ratings__average__lt=(int(selected_rating)+1)) & Q(ratings__average__gte=int(selected_rating)))) &
                                                                       Q(car_current_location__icontains=word)) &
                                                                            Q(
                                                                            (Q(Q(car_drop_off_date__lt=his_pick_up_date)& Q(booked=False))|
                                                                             Q(Q(car_drop_off_date=his_pick_up_date)& Q(booked=True)))
                                                                            )
                                                                      ).order_by("car_price_perday")
                    elif selected_rating is not None and max_price is None and min_price is None:
                        if int(selected_rating) < 1 or int(selected_rating) > 5:
                            return render(request, 'page404.html', context)
                        context['selected_rating'] = selected_rating
                        context["ResultedCars"] += Car.objects.filter(Q(pending=False)&((Q(ratings__average__lt=(int(selected_rating)+1)) & Q(ratings__average__gte=int(selected_rating))) & Q(car_current_location__icontains=word)) &
                                                                            Q(
                                                                                   (Q(Q(car_drop_off_date__lt=his_pick_up_date)& Q(booked=False))|
                                                                                   Q(Q(car_drop_off_date=his_pick_up_date)& Q(booked=True)))
                                                                            )
                                                                      ).order_by("car_price_perday")
                    elif selected_rating is None and max_price is not None and min_price is not None:
                        context['max_price'] = max_price
                        context['min_price'] = min_price
                        context["ResultedCars"] += Car.objects.filter(Q(pending=False)&((Q(car_price_perday__gte=min_price) & Q(car_price_perday__lte=max_price)) & Q(car_current_location__icontains=word)) & 
                                                                            Q(
                                                                                   (Q(Q(car_drop_off_date__lt=his_pick_up_date)& Q(booked=False))|
                                                                                   Q(Q(car_drop_off_date=his_pick_up_date)& Q(booked=True)))
                                                                            )
                                                                      ).order_by("car_price_perday")
                    else:
                        return render(request, 'page404.html', context)
                else:
                    context["ResultedCars"] += Car.objects.filter(Q(pending=False) & Q(car_current_location__icontains=word) &
                                                                        Q(
                                                                               (Q(Q(car_drop_off_date__lt=his_pick_up_date)& Q(booked=False))|
                                                                               Q(Q(car_drop_off_date=his_pick_up_date)& Q(booked=True)))
                                                                        )
                                                                  ).order_by("car_price_perday")

            # removing duplicates
            context["ResultedCars"] = list(set(context["ResultedCars"]))
            # setting the availability of cars (Note: this cars are gonna be showen, here we're just adding some messages for the user if needed)
            for car in context["ResultedCars"]:
                if his_pick_up_date == car.car_drop_off_date and his_pick_up_time < car.car_drop_off_time:
                    # here we add a message to tell the user that this car is gonna be available in his pick-up-date, but after his pick-up-time, so he's gonna wait
                    car.availability = True
                elif his_pick_up_date == car.car_drop_off_date and his_pick_up_time == car.car_drop_off_time:
                    # here we add a message to tell the user that this car car is gonna be dropped-off at the same time of his pick-up (so he may wait for a bit)
                    car.availability = False

            # this is for the pagination
            page = request.GET.get('?page')
            p = Paginator(context["ResultedCars"], 2)  # here I chose 2 cars per-page just for testing after I'll change it to 10 or smth

            # I'm building the url here in order to use it in the html to move around
            my_url = dict()
            my_url.update(dict({'city': request.GET.get('city')}))
            if 'date' in request.GET:
                my_url.update(dict({'date': request.GET.get('date')}))
                the_date = request.GET.get('date').split()
                numOfDays = date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5])) - date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
                numOfDays = str(numOfDays)
                numOfDays = numOfDays.replace(':', ' ')
                numOfDays = numOfDays.split()
                numOfDays = int(numOfDays[0])
                if numOfDays == 0:
                    numOfDays = 1
                else:
                    numOfDays += 1
            else:
                numOfDays = 1

            if selected_rating is not None:
                my_url.update(dict({'selected_rating': request.GET.get('selected_rating')}))
            if max_price is not None and min_price is not None:
                my_url.update(dict({'max_price': request.GET.get('max_price')}))
                my_url.update(dict({'min_price': request.GET.get('min_price')}))

            params = my_url
            context["Url"] = urllib.parse.urlencode(params)
            context["numofdays"] = numOfDays
            # just to handle errors
            try:
                cars = p.get_page(page)
            except PageNotAnInteger:
                page = 1
                cars = p.get_page(page)
            except EmptyPage:
                page = p.num_pages
                cars = p.get_page(page)

            context["ResultedCars"] = cars

        return render(request, 'car_search.html', context)


def reserving(request):
    context = {}
    if len(request.GET) >= 3 and 'carId' in request.GET and 'city' in request.GET and '?page' in request.GET:
        context["reserved"] = False
        try:
            # if someone tries to input in the url a carid that doesn't exist in db
            id = request.GET.get('carId')
            car = Car.objects.get(car_id=id)
            # here we're checking if the car is in the city
            if request.GET.get('city') in car.car_current_location:
                context["car"] = car
            else:
                return render(request, 'page404.html', context)
        except Exception:
            return render(request, 'page404.html', context)

        if 'date' in request.GET:
            try:
                the_date = request.GET.get('date').split()
                # here we're checking if the date is valid and the car is in the pick-up-location
                if is_date_valid(the_date) is True and request.GET.get('city') == car.car_current_location:
                    if is_still_available(the_date, car) is False:
                        context["reserved"] = True
                else:
                    return render(request, 'page404.html', context)
            except Exception:
                return render(request, 'page404.html', context)

        # I'm building the url here in order to use it in the html to move around
        my_url = dict()
        my_url.update(dict({'city': request.GET.get('city')}))
        my_url.update(dict({'?page': request.GET.get('?page')}))
        if 'date' in request.GET:
            my_url.update(dict({'date': request.GET.get('date')}))
            the_date = request.GET.get('date').split()
            numOfDays = date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5])) - date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
            numOfDays = str(numOfDays)
            numOfDays = numOfDays.replace(':', ' ')
            numOfDays = numOfDays.split()
            numOfDays = int(numOfDays[0])
            if numOfDays == 0:
                numOfDays = 1
            else:
                numOfDays += 1
        else:
            numOfDays = 1

        selected_rating = request.GET.get('selected_rating')
        max_price = request.GET.get('max_price')
        min_price = request.GET.get('min_price')
        if selected_rating is not None:
            my_url.update(dict({'selected_rating': request.GET.get('selected_rating')}))
        if max_price is not None and min_price is not None:
            my_url.update(dict({'max_price': request.GET.get('max_price')}))
            my_url.update(dict({'min_price': request.GET.get('min_price')}))
        params = my_url
        context["Url"] = urllib.parse.urlencode(params)

        amount = (car.car_price_perday * numOfDays)
        context["amount"] = amount
        context["numofdays"] = numOfDays
        return render(request, 'car_reserve.html', context)

    return render(request, 'page404.html', context)


@login_required
def PaymentSuccessful(request, id, the_date, tickets_nb=None):  # here we should make the two following functions generic as we did with checking_before_payment
    if tickets_nb is not None:
        activity = Activity.objects.get(pk=id)
        tickets = Tickets.objects.filter(Q(activity_id=activity.activity_id) & Q(date=the_date)).order_by("date")
        ticket = 1
        if len(tickets) != 0:
            for t in tickets:
                ticket = t
                break
        else:
            return render(request, 'page404.html')

        booking = Activitybooking.objects.create(activity_id=activity, user_id=request.user, booking_date=ticket.date, tickets_nb=tickets_nb, arrival_date=the_date)
        messages.success(request, 'Booking successful!')
        return render(request, 'attractions/success_payment.html')

    try:
        car = Car.objects.get(car_id=id)
    except Exception:
        return render(request, 'page404.html')
    user = request.user
    context = {}

    the_date = urllib.parse.unquote_plus(the_date)  # getting the date from the arguments
    context["car"] = car
    # date validation
    the_date = the_date.split()
    his_pick_up_date = date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
    his_pick_up_time = time(hour=int(the_date[1][1:3]), minute=int(the_date[1][4:6]))
    if is_date_valid(the_date) is False or (car.booked is True and (car.car_drop_off_date != his_pick_up_date or car.car_drop_off_time < his_pick_up_time)) or car.pending is False:
        return render(request, 'page404.html', context)

    if car.booked is True:  # if the car is already booked --> pick-up-time = drop-off-time
        car.car_pick_up_time = car.car_drop_off_time
    else:  # the car isn't booked rn
        car.booked = True
        car.car_pick_up_time = time(int(the_date[1][1:3]), int(the_date[1][4:6]), int(the_date[1][7:9]))

    car.pending = False

    # pick-up date
    car.car_pick_up_date = date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
    # drop-off date
    car.car_drop_off_date = date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5]))
    # drop-off time
    car.car_drop_off_time = time(int(the_date[4][1:3]), int(the_date[4][4:6]), int(the_date[4][7:9]))

    car.save()

    numOfDays = date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5])) - date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
    numOfDays = str(numOfDays)
    numOfDays = numOfDays.replace(':', ' ')
    numOfDays = numOfDays.split()
    numOfDays = int(numOfDays[0])
    if numOfDays == 0:
        numOfDays = 1
    else:
        numOfDays += 1

    amount = (car.car_price_perday * numOfDays)

    # making the invoice
    booking = Carbooking.objects.create(user_id=user, car_id=car, amount=amount, pick_up_date=car.car_pick_up_date, pick_up_time=car.car_pick_up_time, drop_off_date=car.car_drop_off_date, drop_off_time=car.car_drop_off_time)

    # sending the invoice email
    subject = "Check Your Car Reservation Invoice"
    email_html = render_to_string('email_car_invoice.html', {'user': user, 'car': car, 'invoice': booking})
    email_plain = strip_tags(email_html)
    send_mail(
        subject,
        email_plain,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=email_html,
    )

    context["amount"] = amount
    context["numofdays"] = numOfDays
    return render(request, 'payment-success.html', context)


@login_required
def PaymentFailed(request, id, the_date, tickets_nb=None):  # here if the payment failed, we tell the user that his payment failed and we display the same car that he wanted to book
    if tickets_nb is not None:
        tickets_to_book = Tickets.objects.get(activity_id=id, date=the_date)
        tickets_to_book.nba = tickets_to_book.nba+int(tickets_nb)
        tickets_to_book.save()
        # add here email sending
        url = f"/attractions/activities/{tickets_to_book.activity_id.category}/?city={tickets_to_book.activity_id.city}&booking_date={the_date}&booking_failed=1"
        return redirect(url)

    try:
        car = Car.objects.get(car_id=id)
    except Exception:
        return render(request, 'page404.html')
    context = {}
    # when the user gets redirected here ---> pending is True
    if car.pending is False:
        return render(request, 'page404.html', context)
    the_date = urllib.parse.unquote_plus(the_date)
    the_date = the_date.split()
    # here just dealing with different cases for displaying the car
    if is_date_valid(the_date) is True and car.booked is False:
        car.pending = False
        car.save()
        if is_still_available(the_date, car) is True:
            context["reserved"] = False
            context["payment_failed"] = True
            context["car"] = car
            numOfDays = date(int(the_date[3][6:]), int(the_date[3][0:2]), int(the_date[3][3:5])) - date(int(the_date[0][6:]), int(the_date[0][0:2]), int(the_date[0][3:5]))
            numOfDays = str(numOfDays)
            numOfDays = numOfDays.replace(':', ' ')
            numOfDays = numOfDays.split()
            numOfDays = int(numOfDays[0])
            if numOfDays == 0:
                numOfDays = 1
            else:
                numOfDays += 1
            amount = (car.car_price_perday * numOfDays)
            context["amount"] = amount
            context["numofdays"] = numOfDays
            item_name = (car.car_brand + " " + car.car_model)
            item_id = car.car_id
            the_date_for_url = " ".join(the_date)
            the_date_for_url = urllib.parse.quote_plus(the_date_for_url)
            paypal_checkout = PayPalPayment(request, item_id, item_name, amount, the_date_for_url)  # Here u must have two views named 'payment-success' and 'payment-failed' which require 2 arguments (request, id). For handling after payemnt
            paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
            context["paypal"] = paypal_payment
        else:
            context["reserved"] = True
        return render(request, 'car_reserve.html', context)
    return render(request, 'page404.html', context)


def drop_off_confirmation(request, id):  # when the user clicks on 'Confirm' from the drop-off-confirmation-email, he gets redirected to here
    if request.user.is_anonymous is False:
        try:
            booking = Carbooking.objects.get(booking_id=id)
        except Exception:
            return render(request, 'page404.html')
        context = {}
        if int(datetime.now().strftime('%H:%M:%S')[0:2]) <= 22:
            time_now = time(int(datetime.now().strftime(
                '%H:%M:%S')[0:2])+1, int(datetime.now().strftime('%H:%M:%S')[3:5]))
        if booking.car_id.booked is False or booking.car_id.pending is True or booking.drop_off_date != date.today() or (booking.drop_off_date == date.today() and booking.drop_off_time > time_now):
            return render(request, 'page404.html')
        if booking.drop_off_date == booking.car_id.car_drop_off_date and booking.drop_off_time == booking.car_id.car_drop_off_time and booking.pick_up_date == booking.car_id.car_pick_up_date and booking.pick_up_time == booking.car_id.car_pick_up_time:
            booking.car_id.booked = False
            booking.car_id.save()
        context['car'] = booking.car_id
        return render(request, 'rating_page.html', context)
    else:
        return redirect("accounts:login")


def pagenotfound(request, exception, template='page404.html'):
    return render(request, template, status=404)
