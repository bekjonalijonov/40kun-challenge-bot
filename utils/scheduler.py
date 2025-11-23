import asyncio
from datetime import datetime, time, timedelta
import pytz
from config.settings import START_DATE, CHANNEL_ID
from main import send_daily_post

tashkent = pytz.timezone("Asia/Tashkent")

async def scheduler():
    while True:
        now = datetime.now(tashkent)
        start = datetime.strptime(START_DATE, "%Y-%m-%d").date()
        day_num = (now.date() - start).days + 1
        
        next_run = tashkent.localize(datetime.combine(now.date(), time(5, 0)))
        if now >= next_run:
            next_run += timedelta(days=1)
        
        await asyncio.sleep((next_run - now).total_seconds())
        
        if 1 <= day_num <= 40:
            await send_daily_post(day_num)