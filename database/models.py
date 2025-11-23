import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, UniqueConstraint

DATABASE_URL = os.getenv("DATABASE_URL")

# Railway beradigan URL ni to‘g‘ri formatga o‘tkazamiz
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# Agar localda bo‘lsa
if not DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/habit"

print(f"[DB] Ulanish: {DATABASE_URL[:50]}...")  # logda ko‘rinadi

engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Completion(Base):
    __tablename__ = "completions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    day = Column(Integer, nullable=False)
    task = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'day', 'task', name='uix_user_day_task'),)

class DailyPost(Base):
    __tablename__ = "daily_posts"
    day = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Baza muvaffaqiyatli yaratildi!")
