from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from config.settings import TOKEN, CHANNEL_ID, ADMIN_ID
from database.models import AsyncSessionLocal, Completion, init_db
from utils.keyboards import get_daily_keyboard
import asyncio
from datetime import datetime
import pytz

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()
tz = pytz.timezone("Asia/Tashkent")

# Har kunlik vazifalar (1-40 kun)
TASKS = {
    i: [
        "5 daqiqa meditatsiya qilish",
        "10 daqiqa kitob o‘qish",
        "30 daqiqa sport bilan shug‘ullanish"
    ] for i in range(1, 41)
}

async def get_counts(day: int) -> list[int]:
    async with AsyncSessionLocal() as s:
        result = await s.execute(
            select(Completion.task, func.count())
            .where(Completion.day == day)
            .group_by(Completion.task)
        )
        counts = {1: 0, 2: 0, 3: 0}
        for task, cnt in result.all():
            counts[task] = cnt
        return [counts[1], counts[2], counts[3]]

async def send_daily_post(day: int):
    tasks = TASKS[day]
    counts = await get_counts(day)
    
    text = f"""<b>40 KUNLIK ODAT CHALLENGE</b>

<b>Bugun: {day}-kun</b> | {datetime.now(tz).strftime('%d.%m.%Y')}

<b>Vazifalar:</b>
1️⃣ {tasks[0]}
2️⃣ {tasks[1]}
3️⃣ {tasks[2]}

<i>Belgilang va boshqalar bilan birga o‘sing</i>"""
    
    kb = get_daily_keyboard(day, counts)
    msg = await bot.send_message(CHANNEL_ID, text, reply_markup=kb)
    
    async with AsyncSessionLocal() as s:
        s.add(type("DailyPost", (), {"day": day, "message_id": msg.message_id})())
        await s.commit()

@dp.callback_query(F.data.startswith("done_"))
async def callback_done(cb: CallbackQuery):
    if not cb.message: return
    _, task, day = cb.data.split("_")
    task, day = int(task), int(day)
    user_id = cb.from_user.id
    
    async with AsyncSessionLocal() as s:
        exists = await s.get(Completion, (user_id, day, task))
        if exists:
            await cb.answer("Siz allaqachon belgilagansiz!", show_alert=True)
            return
        s.add(Completion(user_id=user_id, day=day, task=task))
        await s.commit()
    
    counts = await get_counts(day)
    await bot.edit_message_reply_markup(CHANNEL_ID, cb.message.message_id, reply_markup=get_daily_keyboard(day, counts))
    await cb.answer("Ajoyib! Davom eting!")

@dp.message(Command("post"))
async def cmd_post(msg):
    if msg.from_user.id != ADMIN_ID: return
    try:
        day = int(msg.text.split()[1])
        await send_daily_post(day)
        await msg.reply(f"{day}-kun post yuborildi")
    except:
        await msg.reply("Masalan: /post 1")

async def on_startup():
    await init_db()
    print("Bot ishga tushdi! 40 kunlik challenge boshlandi")
    asyncio.create_task(auto_daily_post())

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

# ─────────────────────────────────────────────
# HAR KUN SOAT 05:00 DA AVTO POST (Toshkent vaqti)
# ─────────────────────────────────────────────
import asyncio
from datetime import datetime, time, timedelta
import pytz

tashkent = pytz.timezone("Asia/Tashkent")

async def auto_daily_post():
    """Har kuni soat 05:00 da post tashlaydi"""
    while True:
        now = datetime.now(tashkent)
        # Bugungi 05:00 ni hisoblaymiz
        next_run = tashkent.localize(datetime.combine(now.date(), time(5, 0)))
        if now >= next_run:
            next_run += timedelta(days=1)  # ertaga 05:00 ga o‘tkazamiz
        
        # Qancha kutish kerakligini hisoblaymiz
        sleep_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_seconds)
        
        # Hozirgi kun raqamini hisoblaymiz
        start_date = datetime.strptime("2025-11-24", "%Y-%m-%d").date()  # challenge boshlanish sanasi
        day_number = (now.date() - start_date).days + 1
        
        if 1 <= day_number <= 40:
            try:
                await send_daily_post(day_number)
                print(f"Avto post: {day_number}-kun yuborildi")
            except Exception as e:
                print(f"Avto post xatosi: {e}")

# Startup’da ishga tushiramiz
async def on_startup():
    await init_db()
    print("Bot ishga tushdi! 40 kunlik challenge boshlandi")
    # Scheduler vazifasini bu yerda ishga tushiramiz
    asyncio.create_task(auto_daily_post())

if __name__ == "__main__":
    asyncio.run(main())
