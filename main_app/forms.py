from django import forms

class SearchForm(forms.Form):
    decklist = forms.CharField(widget=forms.Textarea, label='Decklist')
    price_minimum = forms.FloatField(label='Price Minimum')