import requests
import time
import re
import difflib

tags = {
    "Mana Generator" : {"T", "add", "mana", 'R', 'B', 'G', 'W', 'U'},
    "Loss of Life (Self)" : {"pay", "life"},
    "Enter The Battlefield" : {"enters", "battlefield"}
}

def mana_generator_effect(card):
    colors = card.get('color_identity')
    print(colors)
    return f"Add {' '.join(colors)}"

def loss_of_life_self_effect(card):
    return "Pay Life"

def enter_the_battlefield_effect(card):
    return "Enters Battlefield"

tag_effects = {
    "Mana Generator": mana_generator_effect,
    "Loss of Life (Self)":loss_of_life_self_effect,
    "Enter The Battlefield":enter_the_battlefield_effect
}

def remove_unneeded_words(text, words_to_remove):
    return ' '.join(word for word in text.split() if word.lower() not in words_to_remove)

def search_cards(query):
    url = f"https://api.scryfall.com/cards/search?q={query}"
    response = requests.get(url)
    time.sleep(0.05)  # Add a 50 ms delay
    
    response_json = response.json()
    
    if 'data' in response_json:
        cards = response_json['data']
        if len(cards) > 0:
            only_usd_cards = [card for card in cards if card["prices"].get('usd') is not None]
            sorted_usd_cards = sort_cards_by_price(only_usd_cards)
            return sorted_usd_cards[0] if len(sorted_usd_cards) > 0 else None
        else:
            return None
    else:
        # Handle the error, e.g., return an error message
        print(f"Unexpected response JSON: {response_json}")
        return f"Error: {response_json.get('message', 'Unknown error')}"
    
def normalize_keyword(keyword):
    return keyword.lower().strip('{}')

def assign_tags(effect, tags):
    words = set(re.findall(r'\b\w+\b|{{[^}]+}}', effect.lower()))
    normalized_words = {normalize_keyword(word) for word in words}
    assigned_tags = []
    
    for tag, keywords in tags.items():
        normalized_keywords = {normalize_keyword(keyword) for keyword in keywords}
        matching_keywords = normalized_words.intersection(normalized_keywords)
        if len(matching_keywords) / len(normalized_keywords) >= 0.5:
            assigned_tags.append(tag)
            
    return assigned_tags

def search_similar_cards(effect, card_type, card_color_identity, order="usd", sort_dir="asc"):
    effect_words = effect.split()
    effect_query = '+'.join(f"oracle%3A%22{word}%22" for word in effect_words)
    type_query = f"type%3A%22{card_type}%22"
    colors = "".join(card_color_identity)
    if card_color_identity != []:
        color_identity_query = f"id%3D{colors.lower()}+-id%3Ac"
        url = f"https://api.scryfall.com/cards/search?order={order}&dir={sort_dir}&q={effect_query}+{type_query}+{color_identity_query}"
    print(url)
    response = requests.get(url)
    time.sleep(0.05)

    response_json = response.json()

    if 'data' in response_json:
        return response_json['data']
    else:
        print(f"Unexpected response JSON: {response_json}")
        return f"Error: {response_json.get('message', 'Unknown error')}"



def similarity_ratio(string1, string2):
    sequence_matcher = difflib.SequenceMatcher(None, string1, string2)
    return sequence_matcher.ratio()

def filter_similar_cards_above_threshold(cards, threshold, initial_card):
    return [(card_name, similarity) for card_name, similarity in cards if similarity >= threshold and card_name != initial_card]

def get_card_prices(cards):
    cards_with_prices = []
    for card_name, _ in cards:
        similar_card = search_cards(card_name)
        if similar_card is not None:
            card_price = similar_card['prices'].get('usd') if similar_card['prices'].get('usd') is not None else 0
            cards_with_prices.append((card_name, float(card_price)))
    return cards_with_prices

def sort_cards_by_price(cards):
    return sorted(cards, key=lambda x: x[1], reverse=True)

    
def GetTaggedSearch(card):
    unneeded_words = {'you', 'may', 'as', 'the', 'if', 'don t', "don't"}
    card_effect = card.get("oracle_text")
    card_name = card.get("name")
    card_color_identity = card.get('color_identity')
    
    simple_effects = [
        remove_unneeded_words(effect.replace(card_name, "").strip(), unneeded_words)
        for effect in re.split(r'[.,;]', card_effect)
    ]

    tagged_effects = [assign_tags(effect, tags) for effect in simple_effects]
    for effect, tags_assigned in zip(simple_effects, tagged_effects):
        simplified_effects = [tag_effects[tag](card) if tag in tag_effects else effect for tag in tags_assigned]
        card_type_line = card.get('type_line')
        split_card_type = card_type_line.split()
        main_card_type = split_card_type[0]
        all_similar_cards = []
        for simplified_effect in simplified_effects:
                similar_cards = search_similar_cards(simplified_effect, main_card_type, card_color_identity)

        for similar_card in similar_cards:
            similar_card_oracle_text = similar_card.get('oracle_text')
            if similar_card_oracle_text is not None:
                similarity = similarity_ratio(simplified_effect, similar_card_oracle_text)
                all_similar_cards.append((similar_card, similarity)) 

    # Calculate the similarity between the initial card's full effect and similar cards' full effect
        all_similar_cards_with_full_effect_similarity = []
        for similar_card, similarity in all_similar_cards:  # Use similar_card directly instead of card_name
            if similar_card is not None:
                similar_card_effect = similar_card.get("oracle_text")
                if similar_card_effect is not None:
                    full_effect_similarity = similarity_ratio(card_effect, similar_card_effect)
                    all_similar_cards_with_full_effect_similarity.append((similar_card, full_effect_similarity))


    similarity_threshold = 0.3
    similar_cards_above_threshold = filter_similar_cards_above_threshold(all_similar_cards_with_full_effect_similarity, similarity_threshold, card)

    # Get card prices
    cards_with_prices = get_card_prices(similar_cards_above_threshold)

    # Sort the array of tuples based on the price
    sorted_similar_cards_by_price = sort_cards_by_price(cards_with_prices)
    sorted_similar_cards = [card_info[0] for card_info in sorted_similar_cards_by_price] 

    return sorted_similar_cards
