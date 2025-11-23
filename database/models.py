# database/models.py – RAILWAY UCHUN 100% ISHONCHLI VERSIYA

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, UniqueConstraint

# Railway DATABASE_URL ni avto beradi, lekin ba'zida kech qoladi
raw_url = os.getenv("DATABASE_URL")

if raw_url and raw_url.startswith("postgres://"):
    DATABASE_URL = raw_url.replace("postgres://", "postgresql+psycopg://", 1)
elif raw_url and raw_url.startswith("postgresql://"):
    DATABASE_URL = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    # Agar Railway hali bermagan bo‘lsa yoki localda bo‘lsa
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/habit"

print(f"DB URL: {DATABASE_URL}")  # ← BU QATORNI QO‘SHDIM, LOGDA KO‘RINADI!

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
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Baza muvaffaqiyatli yaratildi!")
    except Exception as e:
        print(f"Baza yaratishda xato: {e}")
