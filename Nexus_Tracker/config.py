import os
from dotenv import load_dotenv

load_dotenv()

NEXUS_API = os.getenv(
    "NEXUS_API",
    "http://127.0.0.1:8000"
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
)

TIMEZONE = os.getenv(
    "TIMEZONE",
    "America/Monterrey"
)
