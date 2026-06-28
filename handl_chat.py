import asyncio
import logging

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, GROUP_ID
from db import is_user_registered, get_topic_by_user, get_user_by_topic, get_user_data, save_topic, delete_topic_by_user

logger = logging.getLogger(__name__)

router = Router()


async def create_topic_retry(bot, user_id: int, text: str, first_name: str, topic_name: str, retries: int = 6):
    for i in range(retries):
        await asyncio.sleep(10)
        try:
            topic = await bot.create_forum_topic(
                chat_id=GROUP_ID,
                name=topic_name[:128],
            )
            save_topic(user_id, topic.message_thread_id)
            await bot.send_message(
                chat_id=GROUP_ID,
                message_thread_id=topic.message_thread_id,
                text=text,
            )
            logger.info(f"retry success: created topic {topic.message_thread_id} for user {user_id}")
            return
        except Exception as e:
            logger.info(f"retry {i+1}/{retries} failed for user {user_id}: {e}")
    logger.error(f"all retries failed for user {user_id}")


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

    user_id = message.from_user.id
    logger.info(f"user_to_admin: user={user_id}, text={message.text}")

    if GROUP_ID:
        topic_id = get_topic_by_user(user_id)
        logger.info(f"topic_id from DB: {topic_id}")

        if topic_id:
            try:
                await message.bot.send_message(
                    chat_id=GROUP_ID,
                    message_thread_id=topic_id,
                    text=message.text,
                )
                logger.info(f"sent to existing topic {topic_id}")
                return
            except Exception as e:
                logger.error(f"send to topic {topic_id} failed: {e}")
                delete_topic_by_user(user_id)
                topic_id = None

        if not topic_id:
            user_data = get_user_data(user_id)
            if user_data:
                topic_name = (
                    f"{user_data['first_name']} {user_data['last_name']} | "
                    f"{user_data['region']} {user_data['district']} {user_data['school_number']}"
                )
            else:
                topic_name = message.from_user.first_name or "Foydalanuvchi"

            logger.info(f"creating new topic: {topic_name}")
            try:
                topic = await message.bot.create_forum_topic(
                    chat_id=GROUP_ID,
                    name=topic_name[:128],
                )
                save_topic(user_id, topic.message_thread_id)
                logger.info(f"created new topic {topic.message_thread_id}")

                await message.bot.send_message(
                    chat_id=GROUP_ID,
                    message_thread_id=topic.message_thread_id,
                    text=message.text,
                )
                logger.info("sent to new topic")
                return
            except Exception as e:
                logger.error(f"create_forum_topic failed, scheduling retry: {e}")
                asyncio.create_task(create_topic_retry(
                    message.bot, user_id, message.text,
                    message.from_user.first_name, topic_name
                ))

    logger.info(f"fallback to group general for user {user_id}")
    try:
        await message.bot.send_message(
            chat_id=GROUP_ID,
            text=f"💬 {message.from_user.first_name}: {message.text}",
        )
    except Exception as e:
        logger.error(f"fallback to group failed: {e}")
