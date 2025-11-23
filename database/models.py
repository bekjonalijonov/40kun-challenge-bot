# database/models.py – RAILWAY UCHUN 100% ISHLAYDIGAN VERSIYA

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, UniqueConstraint

DATABASE_URL = os.getenv("DATABASE_URL")

# RAILWAY BERAYOTGAN URL – "postgresql://" bilan (psycopg2 uchun)
# Biz uni "postgresql+psycopg://" ga o‘zgartiramiz (psycopg3 uchun)
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# Agar hali ham to‘g‘ri bo‘lmasa – majburan qo‘shib qo‘yamiz
if DATABASE_URL and "+psycopg://" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

print(f"[DB] FINAL URL: {DATABASE_URL[:60]}...")  # logda ko‘rinadi

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
