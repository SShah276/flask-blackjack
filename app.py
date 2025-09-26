from flask import Flask, render_template, request, redirect, url_for, session
from blackjack import deal_card, calculate_hand, determine_result
import json
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.sql import func
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    player_hand = db.Column(db.Text, nullable=False)
    dealer_hand = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.before_request
def create_tables():
    db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login: just capture the username"""
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clear the user session"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/game')
def index():
    """Starts a new game if one doesn't exist."""
    if 'username' not in session:
        return redirect(url_for('login'))

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
    if 'player_hand' not in session:
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
    if 'player_hand' not in session:
        return redirect(url_for('index'))
        
    session['player_turn'] = False
    dealer_hand = session['dealer_hand']
    
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(deal_card())
    
    session['dealer_hand'] = dealer_hand
    session.modified = True
    
    result = determine_result(session['player_hand'], dealer_hand)

    # Save game result to DB
    game = Game(
        username=session['username'],
        player_hand=json.dumps(session['player_hand']),
        dealer_hand=json.dumps(dealer_hand),
        result=result
    )
    db.session.add(game)
    db.session.commit()

    return render_template('index.html',
                         player_hand=session['player_hand'],
                         dealer_hand=dealer_hand,
                         player_total=calculate_hand(session['player_hand']),
                         dealer_total=calculate_hand(dealer_hand),
                         message=result)

@app.route('/new_game')
def new_game():
    session.pop('player_hand', None)
    session.pop('dealer_hand', None)
    session.pop('player_turn', None)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Query this user's games only
    total_games = Game.query.filter_by(username=username).count()
    total_wins = Game.query.filter_by(username=username, result="You win!").count()
    total_losses = Game.query.filter_by(username=username, result="You lose!").count()
    total_draws = Game.query.filter_by(username=username, result="Draw!").count()

    recent_games = Game.query.filter_by(username=username).order_by(Game.timestamp.desc()).limit(10).all()

    win_percentage = round((total_wins / total_games) * 100, 2) if total_games > 0 else 0.0

    return render_template(
        'dashboard.html',
        username=username,
        total_games=total_games,
        total_wins=total_wins,
        total_losses=total_losses,
        total_draws=total_draws,
        recent_games=recent_games,
        win_percentage=win_percentage
    )

@app.route('/reset', methods=['POST'])
def reset_game_stats():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    Game.query.filter_by(username=username).delete()
    db.session.commit()

    return redirect(url_for('dashboard'))

# Removed /reset because dashboard no longer exists
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)


