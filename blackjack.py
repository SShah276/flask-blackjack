import random
# Blackjack functions and logic
def deal_card():
    """Deals a random card from the deck."""
    deck = [2,3,4,5,6,7,8,9,10,
            2,3,4,5,6,7,8,9,10,
            2,3,4,5,6,7,8,9,10,
            2,3,4,5,6,7,8,9,10,
            'J','Q','K','A',
            'J','Q','K','A',
            'J','Q','K','A',
            'J','Q','K','A']
    return random.choice(deck)

def calculate_hand(hand):
    """Calculates the total value of a hand, handling face cards and aces."""
    total = 0
    face = ['J','Q','K']
    aceCount = 0
    for card in hand:
        if card in range(1,11):
            total += card
        elif card in face:
            total+= 10
        elif card == 'A':
            aceCount = 1
    for _ in range(aceCount):
        if total + 11 <= 21:
            total += 11
        else:
            total += 1
    return total

def determine_result(player_hand, dealer_hand):
    """Determines the outcome of the game."""
    player_total = calculate_hand(player_hand)
    dealer_total = calculate_hand(dealer_hand)

    if player_total == 21 and dealer_total == 21:
        return f"Draw! Both have 21."
    elif player_total == 21:
        return f"Blackjack! You win with {player_hand}!"
    elif dealer_total == 21:
        return f"Dealer wins with Blackjack! Dealer had {dealer_hand}."
    elif player_total > 21:
        return f"Bust! You had {player_hand} for a total of {player_total}. You lose!"
    elif dealer_total > 21:
        return f"Dealer busts! Dealer had {dealer_hand} for a total of {dealer_total}. You win!"
    elif 21 - dealer_total < 21 - player_total:
        return f"Dealer wins! Dealer had {dealer_hand} ({dealer_total}), you had {player_hand} ({player_total})."
    else:
        return f"You win! You had {player_hand} ({player_total}), dealer had {dealer_hand} ({dealer_total})."