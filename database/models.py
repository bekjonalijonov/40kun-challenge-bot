# database/models.py  ← TO‘LIQ SHU KODNI JOYLASHTIRING

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, UniqueConstraint

# Railway DATABASE_URL ni avto beradi (postgres:// shaklda)
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway "postgres://" bilan beradi, psycopg esa "postgresql+psycopg://" talab qiladi
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# Agar localda ishlatayotgan bo‘lsangiz
if not DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost/habit"

# Engine yaratamiz
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base
Base = declarative_base()

# Modellar
class Completion(Base):
    __tablename__ = "completions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    day = Column(Integer, nullable=False)
    task = Column(Integer, nullable=False)  # 1,2,3
    __table_args__ = (UniqueConstraint('user_id', 'day', 'task', name='uix_user_day_task'),)

class DailyPost(Base):
    __tablename__ = "daily_posts"
    day = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)

# DB yaratish funksiyasi
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
