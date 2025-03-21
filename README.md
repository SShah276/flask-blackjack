# Flask Blackjack
A simple web-based implementation of the classic Blackjack card game built with Python, HTML, and Flask.

## **Features**

Play the Blackjack card game against a dealer controlled by the computer
Simple and intuitive UI
Session-based gameplay that maintains game state between actions
Dealer plays by standard casino rules (hits until 17)

## Installation
1. Clone this repository
2. Install dependencies:
`pip install flask`
3. Run the application:
`python app.py`

Open your browser and go to [(http://127.0.0.1:5000/)](http://127.0.0.1:5000/)

## How to Play

The game starts with both the player and dealer receiving two cards. 
Choose to "Hit" (receive another card) or "Stand" (end your turn). 
Try to get as close to 21 as possible without going over. 
After you stand, the dealer will play their turn. 
Closest to 21 without going over wins.
Click "New Game" to play again after a session ends.

### Game Rules

Number cards (2-10) are worth their face value.
Face cards (J, Q, K) are worth 10.
Aces can be worth the value of 1 or 11. They are assumed to be worth 11, but if that would cause a bust, they can be worth 1.
Dealer must hit until they have at least 17.
Blackjack (21 with first two cards dealt) beats a regular 21.

### Project Structure

app.py - Main application file with routes and game logic

templates/index.html - HTML template for the game interface


###Future Improvements!

Add betting functionality with money
Implement splitting and doubling down
Add more advanced game statistics
Improve the user interface with card images
