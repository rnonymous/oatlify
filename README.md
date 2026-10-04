# Oatlify 🥛

A small webapp that monitors Oatly product prices at **Albert Heijn** and **Jumbo** (Dutch supermarkets) and sends a **Telegram notification** whenever a price drops.

## Features

- Scrapes current prices from ah.nl and jumbo.com product pages
- Stores full price history in SQLite
- Background scheduler checks prices on a configurable interval
- Sends a Telegram message on every price drop
- Simple web dashboard showing the latest prices per store
- Manual "Check prices now" button + JSON API

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your Telegram credentials
```

### Configure Telegram

1. Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`, and copy the bot token.
2. Send any message to your new bot (e.g. `hi`), then open
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` and copy the `chat.id`.
3. Put both values in `.env`:

```
TELEGRAM_BOT_TOKEN=123456:ABC-your-bot-token
TELEGRAM_CHAT_ID=123456789
```

## Run

```bash
python app.py
```

Then open http://127.0.0.1:5000 — the dashboard shows current prices for each monitored product/store, and the scheduler will notify Telegram on any price drop.

For production:

```bash
gunicorn -w 1 -b 127.0.0.1:5000 app:app
```

(Use a single worker so the background scheduler runs once.)

## API

| Endpoint | Description |
|---|---|
| `GET /api/prices` | Latest price per product/store |
| `GET /api/prices/<product>/<store>` | Price history for one product/store |
| `POST /api/check` | Trigger an immediate price check |

## Monitored products

Products and URLs are defined in `config.py` (`PRODUCTS`) — add or edit any AH/Jumbo product page there. Default set:

- Oatly The Original (vol) 1L
- Oatly Barista Edition
- Oatly The Original Halfvol 1L

## Configuration

| Env var | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | — | Chat that receives notifications |
| `CHECK_INTERVAL_MINUTES` | `60` | Polling interval |
| `DATABASE_PATH` | `oatlify.db` | SQLite file location |
| `PORT` | `5000` | Dev server port |

## Notes

- Price parsers target each store's product page markup; if a store redesigns its pages, update the regexes in `scraper.py`.
- Be considerate with the check interval — both supermarkets' sites are polled on every run.
