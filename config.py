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
    "oatly-original": [
        {
            "store": "ah",
            "name": "Oatly The Original Haverdrank Vol 1L",
            "url": "https://www.prijsprofeet.nl/product/ah_wi548463/oatly-haverdrank-vol",
        },
        {
            "store": "jumbo",
            "name": "Oatly The Original Haverdrank Vol 1L",
            "url": "https://www.jumbo.com/producten/oatly-the-original-haverdrank-vol-1-l-215260KRT",
        },
    ],
    "oatly-barista": [
        {
            "store": "ah",
            "name": "Oatly Haver Barista Edition 1L",
            "url": "https://www.prijsprofeet.nl/product/ah_wi412158/oatly-haver-barista-edition",
        },
        {
            "store": "jumbo",
            "name": "Oatly Barista Edition Oat Drink 1,5L",
            "url": "https://www.jumbo.com/producten/oatly-the-original-barista-edition-oat-drink-large-format-1,5-l-634513PAK",
        },
    ],
    "oatly-halfvol": [
        {
            "store": "ah",
            "name": "Oatly Haverdrank Halfvol 1L",
            "url": "https://www.prijsprofeet.nl/product/ah_wi475225/oatly-haverdrank-halfvol",
        },
        {
            "store": "jumbo",
            "name": "Oatly The Original Haverdrank Halfvol 1L",
            "url": "https://www.jumbo.com/producten/oatly-the-original-haverdrank-halfvol-1-l-215261KRT",
        },
    ],
}
