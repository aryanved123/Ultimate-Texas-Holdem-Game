# 🃏 Ultimate Texas Hold’em Poker

This is a full-stack implementation of **Ultimate Texas Hold’em**, featuring real game logic and a clean, dynamic interface.

Built with:
- ⚛️ React.js (Frontend)
- 🐍 Flask (Backend)
- ♠️ Pure Python (Game logic)

---

## 🚀 Features

- Two-player simulation (Player vs Dealer)
- Real **Ultimate Texas Hold’em rules**
- One-time **Play Bet**: 4x (Pre-Flop), 2x (Flop), 1x (River)
- Dealer must **qualify** with a pair or better
- Full **hand evaluation** system (High Card → Royal Flush)
- **Auto-resolve** after betting: rest of the cards + showdown
- Dynamic UI: only shows buttons based on game stage
- Balance and pot tracking

---

## 📦 Tech Stack

| Layer     | Technology           |
|-----------|----------------------|
| Frontend  | React + CSS          |
| Backend   | Flask + Python       |
| Game Logic | Pure Python (`game.py`) |
| Styling   | Plain CSS (customizable) |

---

## 🛠 Installation

### 🔹 Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask flask-cors
python app.py
