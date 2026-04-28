

# Telegram RPG Bot 🎮

A simple RPG game I built for Telegram. You fight goblins, collect loot, and occasionally lose all your money gambling. Fun times.

## What's this?

My first attempt at making a game bot. It's basically a text RPG where you can:
- Create a character
- Fight enemies (just goblins for now)
- Buy gear from a shop
- Gamble your HP/money on random events
- Lose everything and start over

## Setup

Need Python 3.x and a Telegram bot token from BotFather.
```bash
pip install -r requirements.txt
```

Make a `.env` file with:
```
BOT_TOKEN=your_token_here
```

Then just:
```bash
python main.py
```

## How it works

Uses SQLite to store player data and pyTelegramBotAPI for the Telegram integration. Pretty straightforward.

Commands:
- `/start` - welcome message
- `/register` - make a character  
- `/profile` - your stats and main menu
- `/clear` - reset everything

## Status

It's functional but definitely a work in progress. The combat is pretty basic and there's only one enemy type. Planning to add more stuff when I have time.

**Done:**
- Combat system
- Shop with items
- Inventory
- Save/load player data

**Want to add:**
- Different enemies
- Make the level system actually do something
- More items
- Maybe skills or abilities

