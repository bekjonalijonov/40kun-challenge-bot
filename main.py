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

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

tashkent = pytz.timezone("Asia/Tashkent")

# PREMIUM VAZIFALAR – HAR KUNI BIR XIL
VAZIFALAR = [
    "🏃‍♂️ <b>10 000 qadam yurish</b> (Fitnes tracker orqali tekshiring)",
    "📖 <b>30 daqiqa kitob o'qish</b> (Har qanday kitob – o'zingizni rivojlantiring)",
    "💧 <b>2 litr suv ichish</b> (Sog'lig'ingiz uchun majburiy)"
]

async def get_participants_count(day: int) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(func.distinct(Completion.user_id))).where(Completion.day == day)
        )
        return result.scalar() or 0

async def send_daily_post(day: int):
    participants = await get_participants_count(day)
    text = f"""
🎯 <b>40 KUNLIK ODAT CHALLENGE – {day}-KUN</b>

👥 <b>Hozircha {participants} kishi qo'shildi!</b>

<b>Bugungi 3 ta vazifa (har kuni bir xil):</b>
{VAZIFALAR[0]}
{VAZIFALAR[1]}
{VAZIFALAR[2]}

<i>Har bir vazifa – yangi odat! Boshqalar bilan birga bajaring va natijani ko'ring.</i>

🔥 Pastdagi tugmalardan belgilang:
    """.strip()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1-vazifa bajarildi", callback_data=f"done_{day}_1")],
        [InlineKeyboardButton(text="2-vazifa bajarildi", callback_data=f"done_{day}_2")],
        [InlineKeyboardButton(text="3-vazifa bajarildi", callback_data=f"done_{day}_3")],
        [InlineKeyboardButton(text="📖 Batafsil ma'lumot", url=TELEGRAPH_URL)]
    ])

    msg = await bot.send_message(CHANNEL_ID, text, reply_markup=keyboard)
    
    async with AsyncSessionLocal() as session:
        session.add(DailyPost(day=day, message_id=msg.message_id))
        await session.commit()

@dp.message(Command("post"))
async def cmd_post(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Siz admin emassiz!")
        return
    try:
        day = int(message.text.split()[1])
        if 1 <= day <= 40:
            await send_daily_post(day)
            await message.answer(f"✅ {day}-kun post kanalda joylandi! (Qatnashuvchilar: {await get_participants_count(day)})")
        else:
            await message.answer("1-40 oralig'ida raqam kiriting.")
    except ValueError:
        await message.answer("Foydalanish: /post 1")
    except Exception as e:
        await message.answer(f"Xato: {e}")

@dp.message(Command("test"))
async def cmd_test(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        day = int(message.text.split()[1])
        if 1 <= day <= 40:
            participants = await get_participants_count(day)
            text = f"""
🔥 <b>TEST REJIMI – {day}-KUN</b>

👥 Hozircha {participants} kishi qo'shildi

<b>Vazifalar:</b>
{VAZIFALAR[0]}
{VAZIFALAR[1]}
{VAZIFALAR[2]}

<i>Bu test – kanalga chiqmadi</i>
            """.strip()

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1-vazifa bajarildi", callback_data=f"done_{day}_1")],
                [InlineKeyboardButton(text="2-vazifa bajarildi", callback_data=f"done_{day}_2")],
                [InlineKeyboardButton(text="3-vazifa bajarildi", callback_data=f"done_{day}_3")],
                [InlineKeyboardButton(text="📖 Batafsil", url=TELEGRAPH_URL)]
            ])

            await message.answer(text, reply_markup=keyboard)
            await message.answer("✅ Test muvaffaqiyatli! Endi /post 1 deb kanalda sinang.")
        else:
            await message.answer("1-40 gacha raqam kiriting")
    except ValueError:
        await message.answer("Foydalanish: /test 1")

@dp.callback_query(F.data.startswith("done_"))
async def callback_done(callback: CallbackQuery):
    data_parts = callback.data.split("_")
    day = int(data_parts[1])
    task = int(data_parts[2])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
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
            await callback.answer("✅ Bajarildi! Raqamlar yangilandi.")

    # Postni yangilash (raqamlar oshishi uchun)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DailyPost.message_id).where(DailyPost.day == day))
        message_id = result.scalar()
        if message_id:
            participants = await get_participants_count(day)
            new_text = f"""
🎯 <b>40 KUNLIK ODAT CHALLENGE – {day}-KUN</b>

👥 <b>Hozircha {participants} kishi qo'shildi!</b>

<b>Bugungi 3 ta vazifa:</b>
{VAZIFALAR[0]}
{VAZIFALAR[1]}
{VAZIFALAR[2]}

<i>Har bir vazifa – yangi odat!</i>

🔥 Pastdagi tugmalardan belgilang:
            """.strip()

            await bot.edit_message_text(new_text, CHANNEL_ID, message_id, parse_mode=ParseMode.HTML)

async def auto_daily_post():
    while True:
        now = datetime.now(tashkent)
        next_run = tashkent.localize(datetime.combine(now.date(), datetime.strptime("05:00", "%H:%M").time()))
        if now >= next_run:
            next_run += timedelta(days=1)
        sleep_sec = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_sec)

        today = datetime.now(tashkent).date()
        start_date = datetime(2025, 11, 24).date()
        day_num = (today - start_date).days + 1

        if 1 <= day_num <= 40:
            await send_daily_post(day_num)

async def on_startup():
    await init_db()
    print("🚀 Bot ishga tushdi! Admin ID: " + str(ADMIN_ID) + " | Kanal ID: " + str(CHANNEL_ID))
    asyncio.create_task(auto_daily_post())

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
