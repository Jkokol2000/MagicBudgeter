from django.shortcuts import render
from .forms import SearchForm
from .card_api import search_cards, GetTaggedSearch
import mtg_parser
import re

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def find_cheaper_cards(request):
    if request.method == 'GET' and 'decklist' in request.GET and 'price_minimum' in request.GET:
        decklist = request.GET.get('decklist')
        price_minimum = float(request.GET.get('price_minimum'))

        try:
            cards = mtg_parser.decklist.parse_deck(decklist)
        except:
            print("An Exception occurred")
        else:
            for card in cards: 
                card_name = re.sub(r'^\d\s+', '', card.name)
                scryfall_card = search_cards(card_name)
                if float(scryfall_card["prices"].get("usd")) > price_minimum:
                    print(GetTaggedSearch(scryfall_card))
                else:
                    continue

            return render(request, 'results.html')
    else:
        form = SearchForm()
    return render(request, 'search_input.html', {'form': form})
