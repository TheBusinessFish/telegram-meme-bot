
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A working Telegram bot prototype that fetches memes from Reddit. Tested locally with Telegram Bot API.

## ✨ Key Features
- 🎯 Fetches memes from `r/memes`, `r/dankmemes`, etc.
- ⚡ Real-time filtering by score (min. 5000 upvotes)
- 💾 Local favorites storage
- 🔄 Navigation system (Next/Previous/New)

## 🛠 How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/telegram-meme-bot.git
   cd telegram-meme-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get your Telegram bot token from [@BotFather](https://t.me/BotFather) and Reddit API keys from [Reddit Apps](https://www.reddit.com/prefs/apps)

4. Create `.env` file:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your credentials
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## 🧪 Testing Notes
- The bot was fully tested using a local development environment
- All core features are confirmed working

## 📁 Project Structure
```
.
├── main.py             # Main bot logic
├── .env.example        # Config template
├── requirements.txt    # Dependencies
└── assets/             # Screenshots (optional)
```
> ⚠️ Note: This is a prototype. For production use, additional hosting setup is required.
