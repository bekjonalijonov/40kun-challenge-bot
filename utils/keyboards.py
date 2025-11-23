from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import TELEGRAPH_URL

def get_daily_keyboard(day: int, counts: list[int]):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Batafsil ma'lumot", url=TELEGRAPH_URL)],
        [InlineKeyboardButton(f"1-vazifa bajarildi — {counts[0]}", callback_data=f"done_1_{day}")],
        [InlineKeyboardButton(f"2-vazifa bajarildi — {counts[1]}", callback_data=f"done_2_{day}")],
        [InlineKeyboardButton(f"3-vazifa bajarildi — {counts[2]}", callback_data=f"done_3_{day}")],
    ])