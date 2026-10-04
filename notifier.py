import logging

import requests

from config import Config, TELEGRAM_API

logger = logging.getLogger(__name__)


def send_telegram_message(text):
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured; would send: %s", text)
        return False
    url = TELEGRAM_API.format(token=Config.TELEGRAM_BOT_TOKEN, method="sendMessage")
    payload = {
        "chat_id": Config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.error("Telegram send failed: %s", exc)
        return False


def notify_price_drop(name, store, old_price, new_price, url):
    store_label = {"ah": "Albert Heijn", "jumbo": "Jumbo"}.get(store, store)
    diff = round(old_price - new_price, 2)
    text = (
        f"🥛 <b>Price drop at {store_label}!</b>\n\n"
        f"{name}\n"
        f"Was: € {old_price:.2f}\n"
        f"Now: <b>€ {new_price:.2f}</b> (−€ {diff:.2f})\n\n"
        f"{url}"
    )
    return send_telegram_message(text)
