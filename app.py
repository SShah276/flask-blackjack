from flask import Flask, render_template, request, redirect, url_for, session
from blackjack import deal_card, calculate_hand, determine_result
import json

app = Flask(__name__)
app.secret_key = 'key'

# Routes
@app.route('/')
def index():
    """Starts a new game if one doesn't exist."""
    if 'player_hand' not in session or 'dealer_hand' not in session:
        session['player_hand'] = [deal_card(), deal_card()]
        session['dealer_hand'] = [deal_card(), deal_card()]
        session['player_turn'] = True
    
    return render_template(
        'index.html',
        player_hand=session['player_hand'],
        dealer_hand=session['dealer_hand'],
        player_total=calculate_hand(session['player_hand']),
        message="Hit or Stand?"
    )

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

    return render_template(
        'index.html',
        player_hand=session['player_hand'],
        dealer_hand=dealer_hand,
        player_total=calculate_hand(session['player_hand']),
        dealer_total=calculate_hand(dealer_hand),
        message=result
    )

@app.route('/new_game')
def new_game():
    """Starts a completely new game."""
    session.pop('player_hand', None)
    session.pop('dealer_hand', None)
    session.pop('player_turn', None)
    session.modified = True
    return redirect(url_for('index'))

# Removed /reset because dashboard no longer exists

if __name__ == "__main__":
    app.run(debug=True)
