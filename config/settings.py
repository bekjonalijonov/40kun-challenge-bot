import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/habit")
TELEGRAPH_URL = os.getenv("TELEGRAPH_URL")
START_DATE = "2025-11-24"  # o‘zgartirishingiz mumkin