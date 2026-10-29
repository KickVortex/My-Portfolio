import re

from aiogram import Bot
from aiogram.types import Message, ChatMemberAdministrator

from database import get_id_by_username
from report_cache import get_user_by_number

TIME_PATTERN = re.compile(r"^(\d+)([mhd])$")


def parse_time(time_str: str):
    # парсит время вида 10m / 2h / 1d, возвращает секунды или None
    match = TIME_PATTERN.match(time_str.lower())
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "m":
        seconds = value * 60
    elif unit == "h":
        seconds = value * 60 * 60
    else:
        seconds = value * 60 * 60 * 24

    return seconds


async def resolve_user(message: Message, target_arg: str | None):
    # сначала смотрим не выбрали ли юзера из списка при вводе @
    # телеграм в этом случае сам подставляет text_mention с готовым id,
    # работает даже если у человека нет username
    for entity in message.entities or []:
        if entity.type == "text_mention":
            return entity.user.id

    # дальше - реплай на сообщение человека
    if message.reply_to_message:
        return message.reply_to_message.from_user.id

    if not target_arg:
        return None

    # номер из последнего /report или /people list
    if target_arg.isdigit():
        return get_user_by_number(message.chat.id, int(target_arg))

    # и последний вариант - обычный @username из кэша чата
    return get_id_by_username(message.chat.id, target_arg)


async def bot_has_rights(bot: Bot, chat_id: int) -> bool:
    # проверяем что бот реально админ и может банить/мутить,
    # а не ловим потом ошибку телеграма и гадаем из-за чего она
    member = await bot.get_chat_member(chat_id, bot.id)
    if not isinstance(member, ChatMemberAdministrator):
        return False
    return member.can_restrict_members
