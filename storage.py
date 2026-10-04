import sqlite3
from contextlib import contextmanager

from config import Config

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_key TEXT NOT NULL,
    store TEXT NOT NULL,
    price REAL NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prices_product ON prices(product_key, store, checked_at);
"""


@contextmanager
def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def record_price(product_key, store, price):
    with get_db() as db:
        db.execute(
            "INSERT INTO prices (product_key, store, price) VALUES (?, ?, ?)",
            (product_key, store, price),
        )


def get_last_price(product_key, store):
    with get_db() as db:
        row = db.execute(
            "SELECT price FROM prices WHERE product_key = ? AND store = ? "
            "ORDER BY checked_at DESC, id DESC LIMIT 1",
            (product_key, store),
        ).fetchone()
    return row["price"] if row else None


def get_price_history(product_key, store, limit=50):
    with get_db() as db:
        rows = db.execute(
            "SELECT price, checked_at FROM prices WHERE product_key = ? AND store = ? "
            "ORDER BY checked_at DESC, id DESC LIMIT ?",
            (product_key, store, limit),
        ).fetchall()
    return [{"price": r["price"], "checked_at": r["checked_at"]} for r in rows]


def get_latest_prices():
    result = {}
    with get_db() as db:
        rows = db.execute(
            "SELECT product_key, store, price, checked_at FROM prices p "
            "WHERE id = (SELECT MAX(id) FROM prices p2 "
            "WHERE p2.product_key = p.product_key AND p2.store = p.store)"
        ).fetchall()
    for r in rows:
        result.setdefault(r["product_key"], {})[r["store"]] = {
            "price": r["price"],
            "checked_at": r["checked_at"],
        }
    return result
