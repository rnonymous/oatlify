import os


def _env(key, default=None):
    return os.environ.get(key, default)


class Config:
    SECRET_KEY = _env("SECRET_KEY", "dev-secret-change-me")
    TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = _env("TELEGRAM_CHAT_ID")
    CHECK_INTERVAL_MINUTES = int(_env("CHECK_INTERVAL_MINUTES", "60"))
    DATABASE_PATH = _env("DATABASE_PATH", "oatlify.db")
    PORT = int(_env("PORT", "5000"))


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

PRODUCTS = {
    "barista-1-5l": [
        {
            "store": "ah",
            "name": "Oatly Barista Edition 1,5L",
            "url": "https://www.prijsprofeet.nl/product/ah_wi570853/oatly-biologische-barista-haver",
        },
        {
            "store": "jumbo",
            "name": "Oatly Barista Edition 1,5L",
            "url": "https://www.jumbo.com/producten/oatly-the-original-barista-edition-oat-drink-large-format-1,5-l-634513PAK",
        },
    ],
    "barista-1l": [
        {
            "store": "ah",
            "name": "Oatly Barista Edition 1L",
            "url": "https://www.prijsprofeet.nl/product/ah_wi412158/oatly-haver-barista-edition",
        },
        {
            "store": "jumbo",
            "name": "Oatly Barista Edition 1L",
            "url": "https://www.jumbo.com/producten/oatly-the-original-haver-barista-edition-1-l-184289STK",
        },
    ],
    "barista-light-1l": [
        {
            "store": "ah",
            "name": "Oatly Barista Edition Lighter Taste 1L",
            "url": "https://www.prijsprofeet.nl/product/ah_wi580284/oatly-barista-edition-lighter-taste",
        },
        {
            "store": "jumbo",
            "name": "Oatly Barista Light 1L",
            "url": "https://www.jumbo.com/producten/oatly-the-original-barista-light-haverdrank-1-l-634365PAK",
        },
    ],
}
