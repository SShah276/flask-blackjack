# Flask Blackjack
A simple web-based implementation of the classic Blackjack with game logic built with Python and player game history is stored in a MySQL database using SQLAlchemy.

## **Features**

- Classic Blackjack gameplay logic (Hit, Stand, Bust, Blackjack)<br>
- Dealer plays by standard casino rules (hits below 17)<br>
- Game results saved to a MySQL database with timestamps<br>
- Dashboard with game statistics (wins, losses, draws, win %)<br>
- Ability to reset game statistics<br>
- Built using Flask, SQLAlchemy, and Jinja2 templates


### Game Rules

Number cards (2-10) are worth their face value.
Face cards (J, Q, K) are worth 10.
Aces can be worth the value of 1 or 11. They are assumed to be worth 11, but if that would cause a bust, they can be worth 1.
Dealer must hit until they have at least 17.
Blackjack (21 with first two cards dealt) beats a regular 21.


### Future Improvements!

Add betting functionality with money  
Implement splitting and doubling down  
Add user authentication for tracking individual players  
Improve the UI with Bootstrap or Tailwind  
