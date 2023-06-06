from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='Search cards', max_length=100)
    price_minimum = forms.DecimalField(label='Price Minimum', decimal_places=2, min_value=0)