# main.py – PREMIUM 40 KUNLIK CHALLENGE BOT (2025)

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.settings import TOKEN, CHANNEL_ID, ADMIN_ID, TELEGRAPH_URL
from database.models import AsyncSessionLocal, Completion, DailyPost, init_db
import asyncio
from datetime import datetime
import pytz

# Bot va Dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

tashkent = pytz.timezone("Asia/Tashkent")

# HAR DOIM BIR XIL 3 VAZIFA – PREMIUM FORMATDA
VAZIFALAR = [
    "🏃‍♂️ <b>10 000 qadam yurish</b>",
    "📖 <b>30 daqiqa kitob o‘qish</b>",
    "💧 <b>2 litr suv ichish</b>"
]

async def get_participants_count(day: int) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(func.distinct(Completion.user_id))).where(Completion.day == day)
        )
        return result.scalar() or 0

async def get_user_progress(user_id: int, day: int) -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Completion.task).where(Completion.user_id == user_id, Completion.day == day)
        )
        done = [row[0] for row in result.fetchall()]
        return done

async def update_post(day: int, message_id: int):
    participants = await get_participants_count(day)
    text = f"""
🔥 <b>40 KUNLIK ODAT CHALLENGE</b>

📅 <b>{day}-KUN</b> | {datetime.now(tashkent).strftime("%d %B, %Y")}

👥 <b>Qatnashayotganlar: {participants} kishi</b>

<b>Bugungi vazifalar:</b>
{VAZIFALAR[0]}
{VAZIFALAR[1]}
{VAZIFALAR[2]}

✅ Bajarilganini belgilang:
    """.strip()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{'✅' if i+1 in await get_user_progress(999999999, day) else '🔘'} Vazifa {i+1}", callback_data=f"done_{day}_{i+1}")]
        for i in range(3)
    ] + [[InlineKeyboardButton(text="📋 Batafsil ma’lumot", url=TELEGRAPH_URL)]])
    
    await bot.edit_message_text(text, CHANNEL_ID, message_id, reply_markup=keyboard)

async def send_daily_post(day: int):
    participants = await get_participants_count(day)
    text = f"""
🎯 <b>40 KUNLIK ODAT CHALLENGE – {day}-KUN</b>

👥 <b>Hozircha {participants} kishi qo‘shildi!</b>

<b>Bugungi 3 ta vazifa:</b>
{VAZIFALAR[0]}
{VAZIFALAR[1]}
{VAZIFALAR[2]}

<i>Har bir bajarilgan vazifa – sizni yangi odamga aylantiradi!</i>

🔥 Bajarilganini pastdagi tugmalar orqali belgilang!
    """.strip()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Vazifa 1", callback_data=f"done_{day}_1"),
         InlineKeyboardButton(text="🔘 Vazifa 2", callback_data=f"done_{day}_2")],
        [InlineKeyboardButton(text="🔘 Vazifa 3", callback_data=f"done_{day}_3")],
        [InlineKeyboardButton(text="📋 Challenge haqida to‘liq", url=TELEGRAPH_URL)]
    ])

    msg = await bot.send_message(CHANNEL_ID, text, reply_markup=keyboard)
    
    async with AsyncSessionLocal() as session:
        session.add(DailyPost(day=day, message_id=msg.message_id))
        await session.commit()

@dp.message(Command("post"))
async def cmd_post(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Faqat admin!")
        return
    try:
        day = int(message.text.split()[1])
        if 1 <= day <= 40:
            await send_daily_post(day)
            await message.answer(f"✅ {day}-kun post kanalda joylandi!")
        else:
            await message.answer("1-40 oralig‘ida raqam kiriting")
    except:
        await message.answer("Foydalanish: /post 15")

@dp.callback_query(F.data.startswith("done_"))
async def callback_done(callback: CallbackQuery):
    _, day_str, task_str = callback.data.split("_")
    day, task = int(day_str), int(task_str)
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        # Agar allaqachon bosilgan bo‘lsa – o‘chiramiz
        result = await session.execute(
            select(Completion).where(Completion.user_id == user_id, Completion.day == day, Completion.task == task)
        )
        exists = result.scalar()
        if exists:
            await session.delete(exists)
            await session.commit()
            await callback.answer("❌ Belgini olib tashladingiz")
        else:
            session.add(Completion(user_id=user_id, day=day, task=task))
            await session.commit()
            await callback.answer("✅ Bajarildi!")

    # Postni yangilaymiz
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DailyPost.message_id).where(DailyPost.day == day))
        message_id = result.scalar()
        if message_id:
            await update_post(day, message_id)

    await callback.message.edit_reply_markup(reply_markup=callback.message.reply_markup)

# Har kuni soat 05:00 da avto post
async def auto_daily_post():
    while True:
        now = datetime.now(tashkent)
        next_run = tashkent.localize(datetime.combine(now.date(), datetime.strptime("05:00", "%H:%M").time()))
        if now >= next_run:
            next_run += timedelta(days=1)
        sleep_sec = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_sec)

        today = datetime.now(tashkent).date()
        start_date = datetime(2025, 11, 24).date()  # challenge boshlanish sanasi
        day_num = (today - start_date).days + 1

        if 1 <= day_num <= 40:
            await send_daily_post(day_num)

async def on_startup():
    await init_db()
    print("🚀 40 kunlik PREMIUM challenge bot ishga tushdi!")
    asyncio.create_task(auto_daily_post())

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
