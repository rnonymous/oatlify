import logging
import threading
import time

import requests

from config import Config, PRODUCTS, TELEGRAM_API
from storage import get_latest_prices

logger = logging.getLogger(__name__)

POLL_INTERVAL = 25

STORE_LABELS = {"ah": "Albert Heijn", "jumbo": "Jumbo"}

HELP_TEXT = (
    "🥛 Oatlify price monitor\n\n"
    "/price — current prices per product and store\n"
    "/lowest — the single lowest price right now\n"
    "/help — this message"
)


def _tg(method, payload):
    if not Config.TELEGRAM_BOT_TOKEN:
        return None
    url = TELEGRAM_API.format(token=Config.TELEGRAM_BOT_TOKEN, method=method)
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error("Telegram %s failed: %s", method, exc)
        return None


def _current_prices_text():
    latest = get_latest_prices()
    lines = []
    overall_lowest = None
    for key, entries in PRODUCTS.items():
        store_prices = []
        for entry in entries:
            info = latest.get(key, {}).get(entry["store"])
            if info:
                store_prices.append((entry["store"], info["price"], entry))
        if not store_prices:
            lines.append(f"{key}: no data yet")
            continue
        lowest = min(store_prices, key=lambda s: s[1])
        if overall_lowest is None or lowest[1] < overall_lowest[1]:
            overall_lowest = lowest
        parts = []
        for store, price, _ in store_prices:
            label = STORE_LABELS.get(store, store)
            mark = " ✅" if (store, price) == (lowest[0], lowest[1]) else ""
            parts.append(f"{label} €{price:.2f}{mark}")
        lines.append(f"<b>{lowest[2]['name']}</b>\n" + " | ".join(parts))
    text = "🥛 <b>Current Oatly prices</b>\n\n" + "\n\n".join(lines)
    if overall_lowest:
        store, price, entry = overall_lowest
        label = STORE_LABELS.get(store, store)
        text += (
            f"\n\n🏆 Lowest overall: <b>{entry['name']}</b> at "
            f"{label} — <b>€{price:.2f}</b>"
        )
    return text


def _lowest_text():
    latest = get_latest_prices()
    best = None
    for key, entries in PRODUCTS.items():
        for entry in entries:
            info = latest.get(key, {}).get(entry["store"])
            if info and (best is None or info["price"] < best[0]):
                best = (info["price"], entry, entry["store"])
    if best is None:
        return "No price data yet — wait for the first check."
    price, entry, store = best
    label = STORE_LABELS.get(store, store)
    return (
        f"🏆 <b>Lowest Oatly price right now</b>\n\n"
        f"{entry['name']}\n"
        f"{label}: <b>€{price:.2f}</b>\n\n{entry['url']}"
    )


def handle_command(text):
    text = text.strip().lower()
    if text in ("/start", "/help", "help"):
        return HELP_TEXT
    if text.startswith("/price"):
        return _current_prices_text()
    if text.startswith("/lowest"):
        return _lowest_text()
    return None


def _poll_loop():
    offset = 0
    while True:
        try:
            payload = {"timeout": POLL_INTERVAL, "offset": offset}
            result = _tg("getUpdates", payload)
            if not result or not result.get("ok"):
                time.sleep(5)
                continue
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or update.get("edited_message")
                if not message or not message.get("text"):
                    continue
                reply = handle_command(message["text"])
                if reply:
                    _tg(
                        "sendMessage",
                        {
                            "chat_id": message["chat"]["id"],
                            "text": reply,
                            "parse_mode": "HTML",
                        },
                    )
        except Exception:
            logger.exception("Bot poll loop error")
            time.sleep(5)


def start_bot():
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.info("Telegram not configured; bot commands disabled")
        return
    thread = threading.Thread(target=_poll_loop, daemon=True, name="tg-bot")
    thread.start()
    logger.info("Telegram bot command listener started")
