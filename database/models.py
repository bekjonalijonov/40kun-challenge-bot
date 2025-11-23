# database/models.py – RAILWAY UCHUN TO‘G‘RI VERSIYA

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, UniqueConstraint

# Railway DATABASE_URL ni avto beradi
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway "postgres://" bilan beradi → "postgresql+psycopg://" ga o‘zgartiramiz
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
else:
    # Agar localda ishlayotgan bo‘lsa (masalan VS Code’da)
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/habit"

# Engine yaratamiz
engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

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
    task = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'day', 'task', name='uix_user_day_task'),)

class DailyPost(Base):
    __tablename__ = "daily_posts"
    day = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)

# DB yaratish
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
