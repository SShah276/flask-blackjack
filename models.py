from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from app import app

db = SQLAlchemy(app)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    player_hand = db.Column(db.Text, nullable=False)
    dealer_hand = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

