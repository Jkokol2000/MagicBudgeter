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
        card_results = {}

        try:
            cards = mtg_parser.decklist.parse_deck(decklist)
        except:
            print("An Exception occurred")
        else:
            for card in cards:
                card_name = re.sub(r'^\d\s+', '', card.name)
                scryfall_card = search_cards(card_name)
                if scryfall_card['prices']['usd'] is not None and float(scryfall_card['prices']['usd']) > price_minimum:
                    similarCards = GetTaggedSearch(scryfall_card)
                    cheaper_cards = [card for card in similarCards if float(card['prices']["usd"]) < price_minimum]

                    # Sort the cheaper cards by USD price, from highest to lowest
                    sorted_cheaper_cards = sorted(cheaper_cards, key=lambda card: float(card['prices']['usd']), reverse=True)

                    card_results[scryfall_card['name']] = (scryfall_card, sorted_cheaper_cards)
                else:
                    continue

            return render(request, 'results.html', {'card_results': card_results})
    else:
        form = SearchForm()
    return render(request, 'search_input.html', {'form': form})


