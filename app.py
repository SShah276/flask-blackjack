from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'key'

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

# Routes
@app.route('/')
def index():
    """Starts a new game if one doesn't exist."""
    if 'player_hand' not in session or 'dealer_hand' not in session:
        session['player_hand'] = [deal_card(), deal_card()]
        session['dealer_hand'] = [deal_card(), deal_card()]
        session['player_turn'] = True
    
    return render_template('index.html',
                         player_hand=session['player_hand'],
                         dealer_hand=session['dealer_hand'],
                         player_total=calculate_hand(session['player_hand']),
                         message="Hit or Stand?")

@app.route('/hit')
def hit():
    """Handles the player hitting for another card."""
    if 'player_hand' not in session or 'dealer_hand' not in session:
        # If session data is missing, redirect to start a new game
        return redirect(url_for('index'))
        
    if session.get('player_turn', True):
        session['player_hand'].append(deal_card())
        player_total = calculate_hand(session['player_hand'])
        
        if player_total >= 21:
            session['player_turn'] = False
            return redirect(url_for('stand'))
    
    # Make sure to store the modified session data
    session.modified = True
    return redirect(url_for('index'))

@app.route('/stand')
def stand():
    """Handles the dealer's turn and ends the round."""
    if 'player_hand' not in session or 'dealer_hand' not in session:
        return redirect(url_for('index'))
        
    session['player_turn'] = False
    dealer_hand = session['dealer_hand']
    
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(deal_card())
    
    session['dealer_hand'] = dealer_hand
    session.modified = True
    
    result = determine_result(session['player_hand'], dealer_hand)
    
    return render_template('index.html',
                         player_hand=session['player_hand'],
                         dealer_hand=dealer_hand,
                         player_total=calculate_hand(session['player_hand']),
                         dealer_total=calculate_hand(dealer_hand),
                         message=result)

@app.route('/new_game')
def new_game():
    """Starts a completely new game."""
    session.pop('player_hand', None)
    session.pop('dealer_hand', None)
    session.pop('player_turn', None)
    session.modified = True
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
