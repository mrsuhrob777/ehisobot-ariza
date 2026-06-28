from aiogram import Router, types
from aiogram.filters import Command

from config import ADMIN_ID
from db import count_users

router = Router()

COMMANDS = (
    "/start - Botni ishga tushirish\n"
    "/register - Ro'yxatdan o'tish\n"
    "/cancel - Jarayonni bekor qilish\n"
    "/member - Ariza sonini ko'rish (guruh)\n"
    "/getgroupid - Guruh ID sini olish"
)


@router.message(Command("getgroupid"))
async def cmd_get_group_id(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"Guruh ID: <code>{message.chat.id}</code>")


@router.message(Command("member"))
async def cmd_member(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    count = count_users()
    await message.answer(f"📊 Arizalar soni: <b>{count}</b>")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    if message.chat.type == "private" or message.from_user.id == ADMIN_ID:
        await message.answer(f"Mavjud buyruqlar:\n\n{COMMANDS}")


@router.message(lambda msg: msg.text and msg.text.strip() == "/")
async def cmd_slash(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"Mavjud buyruqlar:\n\n{COMMANDS}")
