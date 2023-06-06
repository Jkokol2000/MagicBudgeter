import requests

def search_cards(query):
    url = f"https://api.scryfall.com/cards/search?q={query}"
    response = requests.get(url)
    cards = response.json()['data']
    return cards