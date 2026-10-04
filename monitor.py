import logging

from config import PRODUCTS
from notifier import notify_price_drop
from scraper import PriceNotFoundError, scrape
from storage import get_last_price, record_price

logger = logging.getLogger(__name__)


def check_all_products():
    results = []
    for product_key, entries in PRODUCTS.items():
        for entry in entries:
            store = entry["store"]
            try:
                price = scrape(store, entry["url"])
            except Exception as exc:
                logger.error(
                    "Failed to scrape %s at %s: %s", product_key, store, exc
                )
                continue

            old_price = get_last_price(product_key, store)
            record_price(product_key, store, price)

            dropped = old_price is not None and price < old_price
            if dropped:
                notify_price_drop(
                    entry["name"], store, old_price, price, entry["url"]
                )

            results.append(
                {
                    "product": product_key,
                    "store": store,
                    "name": entry["name"],
                    "price": price,
                    "previous": old_price,
                    "dropped": dropped,
                }
            )
    return results
