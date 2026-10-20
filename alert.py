#!/usr/bin/env python3
"""Daily high-risk meme coin alert, sent to Telegram.

Pulls the CoinGecko meme-token category (free, no API key), keeps smaller coins
that are actually trading, and sends the top few to a Telegram chat.

Environment variables:
  TELEGRAM_BOT_TOKEN   token from @BotFather
  TELEGRAM_CHAT_ID     your chat id (see README)

Usage:
  python3 alert.py             fetch and send
  python3 alert.py --dry-run   fetch and print the message, send nothing
"""
import json
import os
import sys
import urllib.parse
import urllib.request

# ---- Tune these ----------------------------------------------------------
MIN_MCAP = 5_000_000        # below this, liquidity is usually too thin to exit
MAX_MCAP = 150_000_000      # above this it is not "high risk" for this list
MIN_VOLUME_24H = 500_000    # need real trading, not a quiet pool
MIN_TURNOVER = 0.05         # 24h volume / market cap
MAX_24H_GAIN = 150.0        # skip vertical pumps, they are the usual exit trap
HOW_MANY = 5
# --------------------------------------------------------------------------

API = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_coins():
    qs = urllib.parse.urlencode({
        "vs_currency": "usd",
        "category": "meme-token",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "price_change_percentage": "24h,7d",
    })
    req = urllib.request.Request(f"{API}?{qs}", headers={"User-Agent": "meme-alerts/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def select(coins):
    picks = []
    for c in coins:
        mcap = c.get("market_cap") or 0
        vol = c.get("total_volume") or 0
        ch24 = c.get("price_change_percentage_24h_in_currency")
        if ch24 is None:
            ch24 = c.get("price_change_percentage_24h")
        if not (MIN_MCAP <= mcap <= MAX_MCAP):
            continue
        if vol < MIN_VOLUME_24H:
            continue
        turnover = vol / mcap
        if turnover < MIN_TURNOVER:
            continue
        if ch24 is None or ch24 <= 0 or ch24 > MAX_24H_GAIN:
            continue
        picks.append({
            "id": c["id"],
            "symbol": (c.get("symbol") or "").upper(),
            "name": c.get("name") or c["id"],
            "mcap": mcap,
            "vol": vol,
            "turnover": turnover,
            "ch24": ch24,
            "ch7d": c.get("price_change_percentage_7d_in_currency"),
        })
    picks.sort(key=lambda p: p["turnover"], reverse=True)
    return picks[:HOW_MANY]


def money(n):
    if n >= 1e9:
        return f"${n / 1e9:.2f}B"
    if n >= 1e6:
        return f"${n / 1e6:.1f}M"
    if n >= 1e3:
        return f"${n / 1e3:.0f}K"
    return f"${n:.0f}"


def build_message(picks):
    if not picks:
        return "Meme coin alert: nothing passed the filters today."
    lines = ["Meme coin alert (high risk)", ""]
    for i, p in enumerate(picks, 1):
        d7 = p["ch7d"]
        d7s = f"{d7:+.0f}% 7d" if d7 is not None else "7d n/a"
        lines.append(f"{i}. {p['name']} ({p['symbol']})")
        lines.append(
            f"   cap {money(p['mcap'])} | vol {money(p['vol'])} | "
            f"turnover {p['turnover'] * 100:.0f}% | {p['ch24']:+.0f}% 24h, {d7s}"
        )
        lines.append(f"   https://www.coingecko.com/en/coins/{p['id']}")
        lines.append(f"   https://dexscreener.com/search?q={urllib.parse.quote(p['symbol'])}")
    lines += [
        "",
        "Before buying: test a tiny sell, check that liquidity is locked, "
        "check top-holder share (rugcheck.xyz or honeypot.is).",
        "These are the coins most likely to go to zero. Not financial advice.",
    ]
    return "\n".join(lines)


def send_telegram(text):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    body = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.load(r)
    if not resp.get("ok"):
        raise RuntimeError(f"Telegram refused the message: {resp}")


def main():
    dry = "--dry-run" in sys.argv
    msg = build_message(select(fetch_coins()))
    if dry:
        print(msg)
        return
    send_telegram(msg)
    print("Sent.")


if __name__ == "__main__":
    main()
