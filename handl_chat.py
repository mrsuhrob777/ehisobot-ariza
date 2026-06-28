import logging

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, GROUP_ID
from db import is_user_registered, get_topic_by_user, get_user_by_topic, get_user_data, save_topic, delete_topic_by_user

logger = logging.getLogger(__name__)

router = Router()


@router.message(lambda msg: (
    msg.chat.type == "private"
    and msg.from_user
    and msg.from_user.id != ADMIN_ID
    and msg.text
    and is_user_registered(msg.from_user.id)
))
async def user_to_admin(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current is not None:
        return

    if GROUP_ID:
        topic_id = get_topic_by_user(message.from_user.id)

        if topic_id:
            try:
                await message.bot.send_message(
                    chat_id=GROUP_ID,
                    message_thread_id=topic_id,
                    text=message.text,
                )
                return
            except Exception:
                delete_topic_by_user(message.from_user.id)
                topic_id = None

        if not topic_id:
            user_data = get_user_data(message.from_user.id)
            if user_data:
                topic_name = (
                    f"{user_data['first_name']} {user_data['last_name']} | "
                    f"{user_data['region']} {user_data['district']} {user_data['school_number']}"
                )
            else:
                topic_name = message.from_user.first_name or "Foydalanuvchi"

            try:
                topic = await message.bot.create_forum_topic(
                    chat_id=GROUP_ID,
                    name=topic_name[:128],
                )
                save_topic(message.from_user.id, topic.message_thread_id)
                topic_id = topic.message_thread_id
            except Exception as e:
                logger.error(f"create_forum_topic error: {e}")

        if topic_id:
            try:
                await message.bot.send_message(
                    chat_id=GROUP_ID,
                    message_thread_id=topic_id,
                    text=message.text,
                )
                return
            except Exception as e:
                logger.error(f"send_message to topic error: {e}")

    await message.bot.send_message(
        chat_id=ADMIN_ID,
        text=message.text,
    )


@router.message(lambda msg: (
    msg.chat.id == GROUP_ID
    and msg.message_thread_id
    and msg.from_user
    and msg.from_user.id == ADMIN_ID
    and msg.text
))
async def admin_to_user(message: types.Message):
    user_id = get_user_by_topic(message.message_thread_id)
    if not user_id:
        await message.reply("Bu topic ga bog'langan foydalanuvchi topilmadi.")
        return

    try:
        await message.bot.send_message(
            chat_id=user_id,
            text=message.text,
        )
    except Exception as e:
        await message.reply(f"Xatolik: {e}")
