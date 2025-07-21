import re
import json
import asyncio
from urllib.parse import urlparse

from telethon import TelegramClient, events

from config import API_HASH, ALLOWED_EXCHANGES, API_ID

SESSION_NAME = "sessions/tg_parser"

CHANNEL = "@listing_alarm"

print(f"Используется сессия: {SESSION_NAME}.session")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def save_listing(listing):
    try:
        with open("data/new_listings.json", "r") as f:
            listings = json.load(f)
    except FileNotFoundError:
        listings = []

    listings.append(listing)

    with open("data/new_listings.json", "w") as f:
        json.dump(listings, f, indent=2)

def extract_ticker_from_url(url: str) -> str:
    parsed = urlparse(url)
    parts = parsed.path.split('/')
    for part in reversed(parts):
        if part:
            return part
    return ""

def extract_url_from_message(message):
    if message.entities:
        for entity in message.entities:
            if entity.url:
                return entity.url
    return None

def process_text(message):
    text = message.message
    url = extract_url_from_message(message)

    if url is None:
        print("В сообщении нет ссылки")
        return None

    match = re.search(r'([A-Za-z ]+ Futures)', text)
    if not match:
        print("Не удалось найти биржу в тексте")
        return None

    exchange = match.group(1)
    ticker = extract_ticker_from_url(url)

    if any(allowed in exchange for allowed in ALLOWED_EXCHANGES):
        listing = {
            "exchange": exchange,
            "ticker": ticker
        }
        print(f"Найден листинг: {listing}")
        return listing
    else:
        print(f"Биржа {exchange} не в списке разрешённых. Пропуск.")
        return None

@client.on(events.NewMessage(chats=CHANNEL))
async def handler(event):
    print(f"Новое сообщение: {event.raw_text}")

    listing = process_text(event.message)
    if listing:
        await save_listing(listing)

async def main():
    await client.start()
    print("Парсер запущен. Ждём новые сообщения...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
