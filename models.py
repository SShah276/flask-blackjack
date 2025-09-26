from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from app import app

db = SQLAlchemy(app)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    player_hand = db.Column(db.Text)
    dealer_hand = db.Column(db.Text)
    result = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
