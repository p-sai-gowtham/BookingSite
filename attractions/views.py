from django.shortcuts import render
from .models import Activity, Tickets
from django.db.models import Q
from .forms import BookingForm, Dateform
from datetime import date


def home(request):
    context = {}
    return render(request, "attractions/home.html", context)


def activities(request, category):
    if 'a' in request.GET:
        query = request.GET.get('a')
    else:
        query = None

    if 'booking_date' in request.GET:
        booking_date = request.GET.get('booking_date')
    else:
        booking_date = None

    categories = ["Nature", "Adventure", "Culture"]
    if 'city' in request.GET and category in categories:
        city = request.GET.get('city').split()
        # check if the city exists
        available_cities = ["london", "uk", "maldives", "rome", "italy", "usa", "new", "york", "barcelona", "spain", "paris", "france"]
        if city[0].lower() not in available_cities:
            return render(request, 'page404.html')
    else:
        return render(request, 'page404.html')

    city = city[0]
    context = {}
    valid_activities = list()
    valid_activities_dates = list()
    if query is not None and booking_date is not None:
        # if the user uses the search bar
        context['booking_date'] = booking_date
        # getting the activities
        if len(query) == 0 and 'activity_id' in request.GET:
            # here if the query is '' --> that means that we're coming from an error from chekcing before payment
            activities = Activity.objects.filter(Q(city=city) & Q(category=category))

            # if this is true that means we're coming from an error while checking before payment
            activity_id = request.GET.get('activity_id')
            try:
                attraction = Activity.objects.get(pk=activity_id)
            except Exception:
                return render(request, 'page404.html')
            try:
                ticket = Tickets.objects.get(activity_id=activity_id, date=booking_date)
            except Exception:
                return render(request, 'page404.html')

            if 'numt' not in request.GET:
                return render(request, 'page404.html')

            context["available_tickets"] = ticket.nba
            context['tickets_num'] = int(request.GET.get('numt'))
            context['activitytitle'] = attraction.title
            context['activityprice'] = attraction.pricea
            context['activityid'] = attraction.activity_id
            context['actd'] = str(ticket.date)
        else:
            activities = Activity.objects.filter(Q(city=city) & (Q(category=category) & Q(title__icontains=query)))

        # for each activity we getting its tickets that have the date >= booking_date
        for activity in activities:
            tickets = Tickets.objects.filter(Q(activity_id=activity.activity_id) & Q(date=booking_date)).exclude(nba=0).order_by("date")
            # after the query if we got at least a ticket we're gonna show that activity to the user
            if len(tickets) != 0:
                valid_activities.append(activity)
                # here I'm getting the date of availability of that activity
                for ticket in tickets:
                    valid_activities_dates.append(str(ticket.date))
                    break

    else:
        # if the user doesn't use the search bar
        activities = Activity.objects.filter(Q(city=city) & Q(category=category))
        # here I set booking_date to today, cuz the user didn't choose one
        booking_date = date.today()
        for activity in activities:
            tickets = Tickets.objects.filter(Q(activity_id=activity.activity_id) & Q(date__gte=booking_date)).exclude(nba=0).order_by("date")
            if len(tickets) != 0:
                valid_activities.append(activity)
                # here I'm getting the date of availability of that activity
                for ticket in tickets:
                    valid_activities_dates.append(str(ticket.date))
                    break

    context['activities'] = valid_activities
    context['dates'] = valid_activities_dates
    context['activities_with_dates'] = zip(valid_activities, valid_activities_dates)
    context['query'] = query
    context['category'] = category
    context['city'] = city
    context['booking_date'] = request.GET.get('booking_date')
    form = BookingForm()
    context['form'] = form

    dateform = Dateform()
    context["dateform"] = dateform

    return render(request, "attractions/result_city.html", context)
