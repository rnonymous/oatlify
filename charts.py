import io
import math
from datetime import datetime

from storage import get_price_history

W = 560
H = 220
PAD_L = 46
PAD_R = 14
PAD_T = 16
PAD_B = 30

STORE_COLORS = {"ah": "#0b7a3e", "jumbo": "#c62828"}
FALLBACK_COLOR = "#0b6bcb"


def _escape(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt_ts(ts):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(ts, fmt).strftime("%d %b %H:%M")
        except (ValueError, TypeError):
            continue
    return ts


def price_chart_svg(product_key, store, limit=40):
    history = get_price_history(product_key, store, limit=limit)
    history.reverse()
    if len(history) < 2:
        return _no_data_svg()

    prices = [h["price"] for h in history]
    lo = min(prices)
    hi = max(prices)
    if hi == lo:
        hi = lo + 0.5
        lo -= 0.5
    span = hi - lo

    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B

    def x(i):
        return PAD_L + (plot_w * i / (len(history) - 1))

    def y(p):
        return PAD_T + plot_h * (1 - (p - lo) / span)

    color = STORE_COLORS.get(store, FALLBACK_COLOR)

    pts = [(x(i), y(h["price"])) for i, h in enumerate(history)]
    path = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    area = (
        f"{path} L {pts[-1][0]:.1f} {PAD_T + plot_h} "
        f"L {pts[0][0]:.1f} {PAD_T + plot_h} Z"
    )
    fill = color + "22"

    grid = []
    for k in range(3):
        val = lo + span * k / 2
        gy = y(val)
        grid.append(
            f'<line x1="{PAD_L}" y1="{gy:.1f}" x2="{W - PAD_R}" y2="{gy:.1f}" '
            f'stroke="#e2e8ee" stroke-width="1"/>'
            f'<text x="{PAD_L - 6}" y="{gy + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#8195a6">€{val:.2f}</text>'
        )

    dots = "".join(
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{color}">'
        f"<title>{_escape(_fmt_ts(h['checked_at']))} — €{h['price']:.2f}</title>"
        f"</circle>"
        for (px, py), h in zip(pts, history)
    )

    first, last = history[0], history[-1]
    trend = last["price"] - first["price"]
    trend_label = f"€{last['price']:.2f}"
    if trend < 0:
        trend_label += f" (−€{abs(trend):.2f} since first check)"
    elif trend > 0:
        trend_label += f" (+€{trend:.2f} since first check)"
    else:
        trend_label += " (no change)"

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, Segoe UI, Roboto, sans-serif">'
        f'<rect width="{W}" height="{H}" fill="#ffffff" rx="8"/>'
        f"{grid[0] if grid else ''}"
        f"{grid[1] if len(grid) > 1 else ''}"
        f"{grid[2] if len(grid) > 2 else ''}"
        f'<path d="{area}" fill="{fill}"/>'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round"/>'
        f"{dots}"
        f'<text x="{W - PAD_R}" y="{H - 8}" text-anchor="end" font-size="11" '
        f'fill="#8195a6">{_escape(trend_label)}</text>'
        f'<text x="{PAD_L}" y="{H - 8}" font-size="11" fill="#8195a6">'
        f"{_escape(_fmt_ts(first['checked_at']))}</text>"
        f'<text x="{W - PAD_R}" y="{H - 8}" text-anchor="end" font-size="11" '
        f'fill="#41586b" font-weight="600"></text>'
        f"</svg>"
    )


def _no_data_svg():
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, Segoe UI, Roboto, sans-serif">'
        f'<rect width="{W}" height="{H}" fill="#f6f8fa" rx="8"/>'
        f'<text x="{W / 2}" y="{H / 2}" text-anchor="middle" font-size="13" '
        f'fill="#8195a6">Not enough price history yet</text>'
        f"</svg>"
    )
