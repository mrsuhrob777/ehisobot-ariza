from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db import is_user_registered
from handl_register import RegisterFSM

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if is_user_registered(message.from_user.id):
        await message.answer(
            "Siz avval ro'yxatdan o'tgansiz. ✅\n\n"
            "Admin siz bilan bog'lanadi. Iltimos, kuting."
        )
        return

    await state.set_state(RegisterFSM.region)
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Pro versiyani olish uchun quyidagi ma'lumotlarni kiriting."
    )
    await message.answer("Viloyatingizni kiriting:")
