import asyncio
import json
import os
from config import SPREAD_THRESHOLD, ALERT_COOLDOWN
from time import time

DATA_DIR = "./data"

SUBSCRIBERS_PATH = os.path.join(DATA_DIR, "subscribers.json")
LISTINGS_PATH = os.path.join(DATA_DIR, "new_listings.json")

async def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_PATH):
        with open(SUBSCRIBERS_PATH, "w") as f:
            json.dump([], f)
    with open(SUBSCRIBERS_PATH, "r") as f:
        return set(json.load(f))

async def save_subscribers(subscribers):
    with open(SUBSCRIBERS_PATH, "w") as f:
        json.dump(list(subscribers), f)

async def load_listings():
    try:
        with open(LISTINGS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def normalize_ticker(ticker: str) -> str:
    return ticker.replace("_", "").replace("-", "").upper()

async def check_spread(bot, client_class_map):
    """
    ClientClassMap: dict вида { 'X': Y, ... }
    """

    last_alert_times = {}

    all_clients = {}

    while True:
        listings = await load_listings()
        subscribers = await load_subscribers()

        ticker_clients = {}

        for listing in listings:
            exchange = listing["exchange"]
            ticker = listing["ticker"]

            if exchange not in client_class_map:
                continue

            normalized_ticker = normalize_ticker(ticker)

            if normalized_ticker not in ticker_clients:
                ticker_clients[normalized_ticker] = {}

            key = (exchange, ticker)
            if key not in all_clients:
                client = client_class_map[exchange](ticker)
                asyncio.create_task(client.connect())
                all_clients[key] = client

            ticker_clients[normalized_ticker][exchange] = all_clients[key]

        now = time()

        for ticker, exchanges in ticker_clients.items():
            prices = {}
            for exchange, client in exchanges.items():
                if client.price is not None:
                    prices[exchange] = client.price

            names = list(prices.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    ex1, ex2 = names[i], names[j]
                    p1, p2 = prices[ex1], prices[ex2]

                    spread = abs((p1 - p2) / ((p1 + p2) / 2)) * 100

                    if spread >= SPREAD_THRESHOLD:
                        key = (ticker, tuple(sorted([ex1, ex2])))
                        last_time = last_alert_times.get(key, 0)

                        if now - last_time > ALERT_COOLDOWN:
                            text = (
                                f"🚨 <b>Спред найден!</b>\n\n"
                                f"Монета: <b>{ticker}</b>\n"
                                f"Спред: {spread:.2f}%\n\n"
                                f"Цена {ex1}: {p1}\n"
                                f"Цена {ex2}: {p2}\n"
                            )
                            for chat_id in subscribers:
                                await bot.send_message(chat_id, text)
                            last_alert_times[key] = now

        await asyncio.sleep(5)
