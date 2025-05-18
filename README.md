# 🤖 Reddit Meme Bot (Local/Test Version)

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

3. Get your credentials:
   - Telegram token: [@BotFather](https://t.me/BotFather)
   - Reddit API: [Reddit Apps](https://www.reddit.com/prefs/apps)

4. Configure environment:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your credentials
   ```

5. Launch the bot:
   ```bash
   python main.py
   ```

## 🧪 Testing Notes
- Successfully tested with Python 3.9+
- Test bot: `@YourTestBot` (local testing only)
- All features verified

## 📁 Project Structure
```text
.
├── main.py             # Main bot logic
├── .env.example        # Config template
├── requirements.txt    # Dependencies
└── assets/             # Screenshots (optional)
```

## 📜 License
MIT License - see [LICENSE](LICENSE) for details.

> ⚠️ Note: Requires local execution. For 24/7 availability, deploy to cloud.
