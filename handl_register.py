from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import GROUP_ID
from db import save_user, save_topic, is_user_registered
from keyboards import subscription_keyboard

router = Router()


class RegisterFSM(StatesGroup):
    region = State()
    district = State()
    school_number = State()
    subscription_type = State()


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await message.answer("Hech qanday jarayon mavjud emas.")
        return
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=types.ReplyKeyboardRemove())


@router.message(StateFilter(RegisterFSM.region))
async def process_region(message: types.Message, state: FSMContext):
    if is_user_registered(message.from_user.id):
        await state.clear()
        await message.answer("Siz avval ro'yxatdan o'tgansiz.")
        return
    await state.update_data(region=message.text)
    await state.set_state(RegisterFSM.district)
    await message.answer("Tumaningizni kiriting:")


@router.message(StateFilter(RegisterFSM.district))
async def process_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(RegisterFSM.school_number)
    await message.answer("Maktab raqamingizni kiriting:")


@router.message(StateFilter(RegisterFSM.school_number))
async def process_school(message: types.Message, state: FSMContext):
    await state.update_data(school_number=message.text)
    await state.set_state(RegisterFSM.subscription_type)
    await message.answer(
        "Obuna turini tanlang:",
        reply_markup=subscription_keyboard,
    )


@router.message(StateFilter(RegisterFSM.subscription_type), F.text.in_({"Butun maktab uchun", "Faqat o'zim uchun"}))
async def process_subscription(message: types.Message, state: FSMContext):
    if is_user_registered(message.from_user.id):
        await state.clear()
        await message.answer("Siz avval ro'yxatdan o'tgansiz.")
        return

    data = await state.update_data(subscription_type=message.text)
    user = message.from_user

    full_data = {
        "telegram_id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "",
        "region": data["region"],
        "district": data["district"],
        "school_number": data["school_number"],
        "subscription_type": data["subscription_type"],
    }

    save_user(full_data)

    await message.answer(
        "Rahmat! Ma'lumotlaringiz qabul qilindi. ✅\n\n"
        "Admin siz bilan bog'lanadi. Iltimos, kuting.",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    topic_name = (
        f"{user.first_name} {user.last_name or ''} | "
        f"{data['region']} {data['district']} {data['school_number']}"
    )

    if GROUP_ID:
        try:
            topic = await message.bot.create_forum_topic(
                chat_id=GROUP_ID,
                name=topic_name[:128],
            )
            save_topic(user.id, topic.message_thread_id)

            username_line = f"📞 Username: @{user.username}" if user.username else "📞 Username: yo'q"
            info_text = (
                f"🆕 Yangi mijoz\n\n"
                f"👤 Ism: {user.first_name} {user.last_name or ''}\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"{username_line}\n"
                f"📍 {data['region']} | {data['district']} | {data['school_number']}\n"
                f"📦 {data['subscription_type']}"
            )
            await message.bot.send_message(
                chat_id=GROUP_ID,
                message_thread_id=topic.message_thread_id,
                text=info_text,
            )
        except Exception as e:
            pass

    await state.clear()


@router.message(StateFilter(RegisterFSM.subscription_type))
async def invalid_subscription(message: types.Message):
    await message.answer(
        "Iltimos, quyidagi tugmalardan birini tanlang:",
        reply_markup=subscription_keyboard,
    )
