import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, jsonify, render_template

from bot import start_bot
from charts import price_chart_svg
from config import Config, PRODUCTS
from monitor import check_all_products
from notifier import send_telegram_message
from storage import get_latest_prices

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

scheduler = BackgroundScheduler(daemon=True)


def scheduled_check():
    try:
        check_all_products()
    except Exception:
        logger.exception("Scheduled check failed")


@scheduler.scheduled_job("interval", minutes=Config.CHECK_INTERVAL_MINUTES, id="price-check")
def scheduled_job():
    scheduled_check()


@app.route("/")
def index():
    latest = get_latest_prices()
    products = []
    for key, entries in PRODUCTS.items():
        stores = []
        for entry in entries:
            store = entry["store"]
            info = latest.get(key, {}).get(store)
            stores.append(
                {
                    "store": store,
                    "name": entry["name"],
                    "url": entry["url"],
                    "price": info["price"] if info else None,
                    "checked_at": info["checked_at"] if info else None,
                }
            )
        products.append({"key": key, "stores": stores})
    return render_template("index.html", products=products)


@app.route("/api/prices")
def api_prices():
    return jsonify(get_latest_prices())


@app.route("/api/prices/<product_key>/<store>")
def api_history(product_key, store):
    from storage import get_price_history

    return jsonify(get_price_history(product_key, store))


@app.route("/api/chart/<product_key>/<store>.svg")
def api_chart(product_key, store):
    svg = price_chart_svg(product_key, store)
    return Response(svg, mimetype="image/svg+xml")


@app.route("/api/check", methods=["POST"])
def api_check():
    results = check_all_products()
    return jsonify(results)


@app.route("/api/notify/test", methods=["POST"])
def api_notify_test():
    text = (
        "🥛 <b>Oatlify test notification</b>\n\n"
        "If you can read this, Telegram notifications are working. "
        "Price drops will look like this.\n\n"
        "<i>Example:</i>\n"
        "Oatly Haver Barista Edition 1L\n"
        "Was: € 2.89\n"
        "Now: <b>€ 1.45</b> (−€ 1.44)"
    )
    ok = send_telegram_message(text)
    if ok:
        return jsonify({"ok": True, "message": "Test notification sent"})
    return (
        jsonify(
            {
                "ok": False,
                "message": "Failed to send — check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
            }
        ),
        500,
    )


scheduler.start()
start_bot()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=Config.PORT, debug=False)
