# main.py – ULTIMATE PREMIUM 40 KUNLIK CHALLENGE BOT (2025)

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.settings import TOKEN, CHANNEL_ID, ADMIN_ID, TELEGRAPH_URL
from database.models import AsyncSessionLocal, Completion, DailyPost, init_db
from sqlalchemy import select, func
import asyncio
from datetime import datetime, timedelta
import pytz

# Bot va Dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
tashkent = pytz.timezone("Asia/Tashkent")

# HAR KUNI BIR XIL 3 VAZIFA – PREMIUM FORMATDA
VAZIFALAR = [
    "Har kuni quyoshdan erta uyg'onish",
    "Har kuni 1000+ istig'for aytish ",
    "Har kuni kitob o'qish (minimal 10 min)"
]

# Har bir vazifani necha kishi bajarganini hisoblash
async def get_task_stats(day: int) -> dict:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Completion.task, func.count()).where(Completion.day == day).group_by(Completion.task)
        )
        stats = {1: 0, 2: 0, 3: 0}
        for task, count in result.fetchall():
            stats[task] = count
        return stats

# Jami qatnashuvchilar (kamida 1 vazifa bajarganlar)
async def get_total_participants(day: int) -> int:
    stats = await get_task_stats(day)
    return sum(stats.values())

# Kanalga post tashlash
async def send_daily_post(day: int):
    stats = await get_task_stats(day)
    total = await get_total_participants(day)

    text = f"""
40 KUNLIK ODAT CHALLENGE – {day}-KUN

Jami <b>{total}</b> kishi bugun vazifalarni bajarishga kirishdi!

Bugungi majburiy 3 vazifa:
• {VAZIFALAR[0]}
• {VAZIFALAR[1]}
• {VAZIFALAR[2]}

Bajarilganlar soni (real-time):
    """.strip()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"1-vazifa bajarildi ✅ {stats[1]}", callback_data=f"done_{day}_1")],
        [InlineKeyboardButton(text=f"2-vazifa bajarildi ✅ {stats[2]}", callback_data=f"done_{day}_2")],
        [InlineKeyboardButton(text=f"3-vazifa bajarildi ✅ {stats[3]}", callback_data=f"done_{day}_3")],
        [InlineKeyboardButton(text="Batafsil ma'lumot", url=TELEGRAPH_URL)]
    ])

    msg = await bot.send_message(CHANNEL_ID, text, reply_markup=keyboard)
    
    async with AsyncSessionLocal() as session:
        session.add(DailyPost(day=day, message_id=msg.message_id))
        await session.commit()

# Tugma bosilganda – real-time yangilash
@dp.callback_query(F.data.startswith("done_"))
async def callback_done(callback: CallbackQuery):
    _, day_str, task_str = callback.data.split("_")
    day = int(day_str)
    task = int(task_str)
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Completion).where(
                Completion.user_id == user_id,
                Completion.day == day,
                Completion.task == task
            )
        )
        exists = result.scalar_one_or_none()

        if exists:
            await session.delete(exists)
            await session.commit()
            await callback.answer("Belgini olib tashladingiz")
        else:
            session.add(Completion(user_id=user_id, day=day, task=task))
            await session.commit()
            await callback.answer("Ajoyib! Hisoblandi")

        # YANGI STATISTIKA
        stats = await get_task_stats(day)
        total = await get_total_participants(day)

        new_text = f"""
40 KUNLIK ODAT CHALLENGE – {day}-KUN

Jami <b>{total}</b> kishi bugun vazifalarni bajarishga kirishdi!

Bugungi majburiy 3 vazifa:
• {VAZIFALAR[0]}
• {VAZIFALAR[1]}
• {VAZIFALAR[2]}

Bajarilganlar soni (real-time):
        """.strip()

        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"1-vazifa bajarildi ✅ {stats[1]}", callback_data=f"done_{day}_1")],
            [InlineKeyboardButton(text=f"2-vazifa bajarildi ✅ {stats[2]}", callback_data=f"done_{day}_2")],
            [InlineKeyboardButton(text=f"3-vazifa bajarildi ✅ {stats[3]}", callback_data=f"done_{day}_3")],
            [InlineKeyboardButton(text="Batafsil ma'lumot", url=TELEGRAPH_URL)]
        ])

        await bot.edit_message_text(
            chat_id=CHANNEL_ID,
            message_id=callback.message.message_id,
            text=new_text,
            reply_markup=new_keyboard
        )

# Admin buyruqlari
@dp.message(Command("post"))
async def cmd_post(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Siz admin emassiz!")
    try:
        day = int(message.text.split()[1])
        if 1 <= day <= 40:
            await send_daily_post(day)
            await message.answer(f"{day}-kun post kanalda joylandi!")
        else:
            await message.answer("1-40 oralig‘ida raqam kiriting")
    except:
        await message.answer("Foydalanish: /post 1")

@dp.message(Command("test"))
async def cmd_test(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        day = int(message.text.split()[1])
        stats = await get_task_stats(day)
        total = await get_total_participants(day)
        text = f"""
TEST – {day}-KUN

Jami: {total} kishi
1-vazifa: {stats[1]}
2-vazifa: {stats[2]}
3-vazifa: {stats[3]}
        """.strip()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"1-vazifa bajarildi ✅ {stats[1]}", callback_data=f"done_{day}_1")],
            [InlineKeyboardButton(text=f"2-vazifa bajarildi ✅ {stats[2]}", callback_data=f"done_{day}_2")],
            [InlineKeyboardButton(text=f"3-vazifa bajarildi ✅ {stats[3]}", callback_data=f"done_{day}_3")],
        ])
        await message.answer(text, reply_markup=keyboard)
    except:
        await message.answer("Foydalanish: /test 1")

# Avto post – har kuni 05:00 da
async def auto_daily_post():
    while True:
        now = datetime.now(tashkent)
        next_run = tashkent.localize(datetime.combine(now.date(), datetime.strptime("05:00", "%H:%M").time()))
        if now >= next_run:
            next_run += timedelta(days=1)
        await asyncio.sleep((next_run - now).total_seconds())

        today = datetime.now(tashkent).date()
        start_date = datetime(2025, 11, 24).date()
        day_num = (today - start_date).days + 1

        if 1 <= day_num <= 40:
            await send_daily_post(day_num)
            print(f"Avto post: {day_num}-kun tashlandi")

# Startup
async def on_startup():
    await init_db()
    print("40 kunlik PREMIUM challenge bot ishga tushdi!")
    asyncio.create_task(auto_daily_post())

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
