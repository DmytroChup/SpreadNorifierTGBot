from os import getenv
from dotenv import load_dotenv

load_dotenv()

# for bot
BOT_TOKEN = getenv("BOT_TOKEN")

# for parser
API_ID = getenv("API_ID")
API_HASH = getenv("API_HASH")

ALLOWED_EXCHANGES = ["MEXC", "Bitget", "BingX", "Gate"]

SPREAD_THRESHOLD = 0
ALERT_COOLDOWN = 300
