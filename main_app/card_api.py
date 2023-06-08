import requests
import time
import re

def remove_unneeded_words(effect, unneeded_words):
    words = re.split(r'\W+', effect)
    filtered_words = [word for word in words if word.lower() not in unneeded_words]
    return ' '.join(filtered_words)

def search_cards(query):
    url = f"https://api.scryfall.com/cards/search?q={query}"
    response = requests.get(url)
    time.sleep(0.05)  # Add a 50 ms delay
    
    response_json = response.json()
    
    if 'data' in response_json:
        cards = response_json['data']
        if len(cards) > 0:
            return cards[0]
        else:
            return None
    else:
        # Handle the error, e.g., return an error message
        print(f"Unexpected response JSON: {response_json}")
        return f"Error: {response_json.get('message', 'Unknown error')}"
    
def GetOracleSearch(card):
    uneeded_words = {'you', 'may', 'as', 'the', 'if', 'don t', "don't"}
    cardEffect = card.get("oracle_text")
    cardName = card.get("name")
    split_effects = re.split(r'[.,;]', cardEffect)
    nameless_effects = [s.replace(cardName,"").strip() for s in split_effects]
    simple_effects = [remove_unneeded_words(effect, uneeded_words) for effect in nameless_effects]
    return simple_effects