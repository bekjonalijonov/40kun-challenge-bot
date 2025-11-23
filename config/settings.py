import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway avto beradi
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost/habit"
TELEGRAPH_URL = os.getenv("TELEGRAPH_URL")
START_DATE = "2025-11-24"  # o‘zgartirishingiz mumkin
