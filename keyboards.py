from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

subscription_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Butun maktab uchun")],
        [KeyboardButton(text="Faqat o'zim uchun")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
