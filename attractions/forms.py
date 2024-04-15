from django import forms
# from bootstrap_daterangepicker import widgets, fields


class BookingForm(forms.Form):
    booking_date = forms.DateField(label="Choose date",widget=forms.DateInput(attrs={'required': '', 'type': 'date','years':range(2024,2030)}))
    num_tickets = forms.IntegerField(label='Number of Tickets', min_value=1)


# I added this for the pop-up
class Dateform(forms.Form):
    pop_booking_date = forms.DateField(label="Choose date",widget=forms.DateInput(attrs={'required': '', 'type': 'date','years':range(2024,2030)}))
