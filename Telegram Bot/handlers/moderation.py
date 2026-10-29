import re
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions

from database import get_rank
from roles import rank_level
from utils import parse_time, resolve_user, bot_has_rights

router = Router()

CAUSE_PATTERN = re.compile(r'cause\s+"([^"]+)"', re.IGNORECASE)
TIME_PATTERN = re.compile(r'\btime\s+(\S+)', re.IGNORECASE)

NO_RIGHTS_TEXT = "У бота нет прав администратора в этом чате, выдайте ему права"
NO_TARGET_TEXT = (
    "Не нашёл пользователя. Выберите его из списка через @, "
    "ответьте на его сообщение, или укажите номер из /report"
)


def get_target_arg(text: str):
    # цель команды - второе слово в сообщении
    # /ban @username ...  или  /ban 2 ...
    parts = text.split(maxsplit=2)
    if len(parts) < 2:
        return None
    return parts[1]


def get_time_arg(text: str):
    match = TIME_PATTERN.search(text)
    if match:
        return match.group(1)
    return None


def get_cause_arg(text: str):
    match = CAUSE_PATTERN.search(text)
    if match:
        return match.group(1)
    return "не указана"


async def check_permission(message: Message, min_rank: str) -> bool:
    caller_rank = get_rank(message.chat.id, message.from_user.id)
    if rank_level(caller_rank) < rank_level(min_rank):
        await message.answer("У вас недостаточно прав для этой команды")
        return False
    return True


async def check_target_rank(message: Message, target_id: int) -> bool:
    # нельзя применять команды к тому у кого ранг равен или выше вашего
    # так админ не сможет забанить владельца, а модер - админа
    caller_rank = get_rank(message.chat.id, message.from_user.id)
    target_rank = get_rank(message.chat.id, target_id)

    if rank_level(target_rank) >= rank_level(caller_rank):
        await message.answer("Нельзя применить это к пользователю с таким же или более высоким рангом")
        return False
    return True


@router.message(Command("mute"))
async def cmd_mute(message: Message):
    if not await check_permission(message, "moder"):
        return

    if not await bot_has_rights(message.bot, message.chat.id):
        await message.answer(NO_RIGHTS_TEXT)
        return

    target_arg = get_target_arg(message.text)
    target_id = await resolve_user(message, target_arg)
    if target_id is None:
        await message.answer(NO_TARGET_TEXT)
        return

    if not await check_target_rank(message, target_id):
        return

    time_arg = get_time_arg(message.text)
    if not time_arg:
        await message.answer("Укажите время, например: /mute @username time 10m")
        return

    seconds = parse_time(time_arg)
    if seconds is None:
        await message.answer("Неверный формат времени, используйте 10m, 2h или 1d")
        return

    until_date = int(time.time()) + seconds

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=target_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_date,
    )

    await message.answer(f"Пользователь замучен на {time_arg}")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not await check_permission(message, "admin"):
        return

    if not await bot_has_rights(message.bot, message.chat.id):
        await message.answer(NO_RIGHTS_TEXT)
        return

    target_arg = get_target_arg(message.text)
    target_id = await resolve_user(message, target_arg)
    if target_id is None:
        await message.answer(NO_TARGET_TEXT)
        return

    if not await check_target_rank(message, target_id):
        return

    time_arg = get_time_arg(message.text)
    if not time_arg:
        await message.answer('Укажите время, например: /ban @username time 10m cause "причина"')
        return

    seconds = parse_time(time_arg)
    if seconds is None:
        await message.answer("Неверный формат времени, используйте 10m, 2h или 1d")
        return

    cause = get_cause_arg(message.text)
    until_date = int(time.time()) + seconds

    await message.bot.ban_chat_member(
        chat_id=message.chat.id,
        user_id=target_id,
        until_date=until_date,
    )

    await message.answer(f"Пользователь забанен на {time_arg}. Причина: {cause}")


@router.message(Command("permban"))
async def cmd_permban(message: Message):
    if not await check_permission(message, "admin"):
        return

    if not await bot_has_rights(message.bot, message.chat.id):
        await message.answer(NO_RIGHTS_TEXT)
        return

    target_arg = get_target_arg(message.text)
    target_id = await resolve_user(message, target_arg)
    if target_id is None:
        await message.answer(NO_TARGET_TEXT)
        return

    if not await check_target_rank(message, target_id):
        return

    cause = get_cause_arg(message.text)

    await message.bot.ban_chat_member(
        chat_id=message.chat.id,
        user_id=target_id,
    )

    await message.answer(f"Пользователь забанен навсегда. Причина: {cause}")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not await check_permission(message, "admin"):
        return

    if not await bot_has_rights(message.bot, message.chat.id):
        await message.answer(NO_RIGHTS_TEXT)
        return

    target_arg = get_target_arg(message.text)
    target_id = await resolve_user(message, target_arg)
    if target_id is None:
        await message.answer(NO_TARGET_TEXT)
        return

    await message.bot.unban_chat_member(
        chat_id=message.chat.id,
        user_id=target_id,
    )

    await message.answer("Пользователь разбанен")
