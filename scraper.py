import re
import json
import logging

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
}

TIMEOUT = 15


class PriceNotFoundError(Exception):
    pass


def _parse_price(raw):
    if raw is None:
        raise PriceNotFoundError("price is None")
    cleaned = re.sub(r"[^\d,\.]", "", str(raw))
    if not cleaned:
        raise PriceNotFoundError(f"no digits in price: {raw!r}")
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    return round(float(cleaned), 2)


def _json_ld_product_price(html):
    for match in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.S,
    ):
        try:
            data = json.loads(match.group(1))
        except (ValueError, TypeError):
            continue
        if isinstance(data, list):
            data = data[0] if data else {}
        if data.get("@type") == "Product":
            offer = data.get("offers") or {}
            if isinstance(offer, list):
                offer = offer[0] if offer else {}
            if "price" in offer:
                return _parse_price(offer["price"])
    return None


def scrape_jumbo(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    html = resp.text

    price = _json_ld_product_price(html)
    if price is not None:
        return price

    price_match = re.search(
        r"Prijs:.*?<[^>]*>.*?(\d+[,.]\d{1,2})", html, re.S
    )
    if price_match:
        return _parse_price(price_match.group(1))

    raise PriceNotFoundError(f"no price found on Jumbo page: {url}")


def scrape_ah_prijsprofeet(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    html = resp.text

    price = _json_ld_product_price(html)
    if price is not None:
        return price

    banner = re.search(
        r'expired-banner--current-price.*?<strong>.*?€\s*(\d+[,.]\d{2})',
        html,
        re.S,
    )
    if banner:
        return _parse_price(banner.group(1))

    raise PriceNotFoundError(f"no price found on PrijsProfeet page: {url}")


SCRAPERS = {"ah": scrape_ah_prijsprofeet, "jumbo": scrape_jumbo}


def scrape(store, url):
    scraper = SCRAPERS.get(store)
    if scraper is None:
        raise PriceNotFoundError(f"unknown store: {store}")
    return scraper(url)
