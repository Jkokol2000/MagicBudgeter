from django.shortcuts import render
from .forms import SearchForm
from .card_api import search_cards

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def find_cheaper_cards(request):
    if request.method == 'GET' and 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            price_minimum = form.cleaned_data['query']
            try:
                price_minimum = float(request.GET.get('price_minimum').replace(',', ''))
            except ValueError:
                price_minimum = 5.0

            cards = search_cards(query)
            cheaper_cards = [card for card in cards if card['prices'].get('usd') and float(card['prices']['usd']) <= price_minimum]

            return render(request, 'results.html', {'cheaper_cards': cheaper_cards})
    else:
        form = SearchForm()
    return render(request, 'search_input.html', {'form': form})