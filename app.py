from flask import Flask, render_template, request, redirect, url_for, session
from blackjack import deal_card, calculate_hand, determine_result
import json
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.sql import func
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///local_blackjack.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    player_hand = db.Column(db.Text, nullable=False)
    dealer_hand = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(200), nullable=False)  # Increased size for longer messages
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Make calculate_hand available in templates
app.jinja_env.globals.update(calculate_hand=calculate_hand)

# Routes
@app.before_request
def create_tables():
    db.create_all()

# ADD THIS ROOT ROUTE - this fixes the "Not Found" error
@app.route('/')
def home():
    """Root route - redirect to login if not logged in, otherwise to game"""
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

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
        
        # Check for immediate blackjack
        player_total = calculate_hand(session['player_hand'])
        dealer_total = calculate_hand(session['dealer_hand'])
        
        if player_total == 21 and dealer_total == 21:
            session['player_turn'] = False
            result = determine_result(session['player_hand'], session['dealer_hand'])
            session['message'] = result
            # Save the game
            game = Game(
                username=session['username'],
                player_hand=json.dumps(session['player_hand']),
                dealer_hand=json.dumps(session['dealer_hand']),
                result=result
            )
            db.session.add(game)
            db.session.commit()
        elif player_total == 21:
            session['player_turn'] = False
            session['message'] = "Blackjack! You have 21!"
            # Let the dealer play
            return redirect(url_for('stand'))
        else:
            session['message'] = "Hit or Stand?"
    
    return render_template('index.html')

@app.route('/hit', methods=['GET', 'POST'])
def hit():
    if 'player_hand' not in session:
        return redirect(url_for('index'))
        
    if session.get('player_turn', True):
        session['player_hand'].append(deal_card())
        player_total = calculate_hand(session['player_hand'])
        
        if player_total > 21:
            session['player_turn'] = False
            # Use your existing determine_result function for bust handling
            result = determine_result(session['player_hand'], session['dealer_hand'])
            session['message'] = result
            
            # Save losing game to DB
            game = Game(
                username=session['username'],
                player_hand=json.dumps(session['player_hand']),
                dealer_hand=json.dumps(session['dealer_hand']),
                result=result
            )
            db.session.add(game)
            db.session.commit()
            
        elif player_total == 21:
            session['player_turn'] = False
            return redirect(url_for('stand'))
        else:
            session['message'] = "Hit or Stand?"
    
    session.modified = True
    return redirect(url_for('index'))

@app.route('/stand', methods=['GET', 'POST'])
def stand():
    if 'player_hand' not in session:
        return redirect(url_for('index'))
        
    session['player_turn'] = False
    dealer_hand = session['dealer_hand']
    
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(deal_card())
    
    session['dealer_hand'] = dealer_hand
    result = determine_result(session['player_hand'], dealer_hand)
    session['message'] = result
    session.modified = True

    # Save game result to DB
    game = Game(
        username=session['username'],
        player_hand=json.dumps(session['player_hand']),
        dealer_hand=json.dumps(dealer_hand),
        result=result
    )
    db.session.add(game)
    db.session.commit()

    return render_template('index.html')

@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    session.pop('player_hand', None)
    session.pop('dealer_hand', None)
    session.pop('player_turn', None)
    session.pop('message', None)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Query this user's games only
    total_games = Game.query.filter_by(username=username).count()
    
    # Updated queries to match your actual result strings
    # Wins: Look for "You win" or "Blackjack! You win"
    total_wins = Game.query.filter(
        Game.username == username,
        db.or_(
            Game.result.like('%You win!%'),
            Game.result.like('%You win.%'),
            Game.result.like('%Blackjack! You win%')
        )
    ).count()
    
    # Losses: Look for "You lose" or "Dealer wins"
    total_losses = Game.query.filter(
        Game.username == username,
        db.or_(
            Game.result.like('%You lose!%'),
            Game.result.like('%You lose.%'),
            Game.result.like('%Dealer wins%')
        )
    ).count()
    
    # Draws: Look for "Draw!"
    total_draws = Game.query.filter(
    Game.username == username,
        db.or_(
            Game.result.like('%Draw!%'),
            Game.result.like('%draw%')
        )
    ).count()
    
    recent_games = Game.query.filter_by(username=username).order_by(Game.timestamp.desc()).limit(10).all()

    win_percentage = round((total_wins / total_games) * 100, 2) if total_games > 0 else 0.0

    # Create stats dictionary matching your template expectations
    stats = {
        'total_games': total_games,
        'wins': total_wins,        
        'losses': total_losses,    
        'total_wins': total_wins,
        'total_losses': total_losses,
        'total_draws': total_draws,
        'win_percentage': win_percentage
    }

    return render_template(
        'dashboard.html',
        username=username,
        stats=stats,
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

# Add this debug route temporarily to check what's being saved
@app.route('/debug_results')
def debug_results():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    games = Game.query.filter_by(username=session['username']).all()
    results = [(game.result, game.timestamp) for game in games]
    return f"<pre>Game results:\n{json.dumps(results, indent=2, default=str)}</pre>"

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)