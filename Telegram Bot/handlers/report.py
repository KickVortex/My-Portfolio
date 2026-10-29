from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import list_cached_users, get_rank, get_owner_id
from report_cache import save_report

router = Router()

RANK_NAMES = {
    "owner": "Владелец",
    "admin": "Админ",
    "moder": "Модератор",
}


def build_user_list(chat_id: int):
    # собирает список всех кого бот видел в чате
    # владелец всегда первый, дальше остальные в порядке кто раньше написал
    # возвращает (строки для вывода, список id в этом же порядке)
    cached = list_cached_users(chat_id)
    if not cached:
        return [], []

    owner_id = get_owner_id(chat_id)

    ordered = []
    if owner_id is not None:
        ordered.append(owner_id)

    for user_id, _username in cached:
        if user_id != owner_id:
            ordered.append(user_id)

    username_by_id = {user_id: username for user_id, username in cached}

    lines = []
    for i, user_id in enumerate(ordered, start=1):
        rank = get_rank(chat_id, user_id)
        label = RANK_NAMES.get(rank, "Участник")
        username = username_by_id.get(user_id)
        name = f"@{username}" if username else f"id{user_id}"
        lines.append(f"{i} - {label} - {name} (id{user_id})")

    return lines, ordered


@router.message(Command("report"))
async def cmd_report(message: Message):
    chat_id = message.chat.id

    lines, ordered = build_user_list(chat_id)
    if not lines:
        await message.answer("Пока никого не видел в этом чате")
        return

    save_report(chat_id, ordered)

    text = "Список пользователей:\n" + "\n".join(lines)
    text += "\n\nМожно забанить/замутить по номеру, например: /ban 2 time 10m cause \"спам\""
    await message.answer(text)
