import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template

from config import Config, PRODUCTS
from monitor import check_all_products
from storage import get_latest_prices, get_price_history

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
    return jsonify(get_price_history(product_key, store))


@app.route("/api/check", methods=["POST"])
def api_check():
    results = check_all_products()
    return jsonify(results)


scheduler.start()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=Config.PORT, debug=False)
