# Telegram AI Bot

A Telegram bot that uses OpenAI's models to respond to messages.

## Features

- Supports multiple AI models:
  - O1 Mini
  - O1 Mini (Sep 12, 2024)
  - GPT-4O
  - GPT-3.5 Turbo (Fallback)
- Model switching via inline keyboard
- Handles long messages
- Simple markdown formatting for responses

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd tgbot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
```
Then edit `.env` and add your:
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- OpenAI API Key

4. Run the bot
```bash
python telegram_bot.py
```

## Usage

- `/start` - Start the bot
- `/model` - Change AI model
- Send any message to get an AI response

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

- `TELEGRAM_API_TOKEN`: Your Telegram bot token from @BotFather
- `OPENAI_API_KEY`: Your OpenAI API key

Never commit the `.env` file with real credentials!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This means you can:
- ✓ Use this code commercially
- ✓ Modify the code
- ✓ Distribute the code
- ✓ Use it privately
- ✓ Sublicense the code

The only requirement is that you include the original license and copyright notice in any copy of the software/source.
