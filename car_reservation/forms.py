from django import forms
from bootstrap_daterangepicker import widgets, fields


class SearchCarsForm(forms.Form):
    date = fields.DateTimeRangeField(
        input_formats=['%m/%d/%Y (%H:%M:%S)'],
        widget=widgets.DateTimeRangeWidget(
            format='%m/%d/%Y (%H:%M:%S)'
        )
    )
