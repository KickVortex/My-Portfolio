from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import get_rank, owner_exists
from roles import rank_level

router = Router()

RANK_TITLES = {
    None: "нет ранга (обычный участник)",
    "moder": "Модератор",
    "admin": "Админ",
    "owner": "Владелец",
}

# команда и с какого ранга она доступна
# None = доступна вообще всем
COMMANDS = [
    (None, "/help", "показать это сообщение"),
    ("moder", "/mute @user time 10m", "замутить человека"),
    ("admin", "/ban @user time 10m cause \"причина\"", "забанить на время"),
    ("admin", "/permban @user cause \"причина\"", "забанить навсегда"),
    ("admin", "/unban @user", "снять бан"),
    ("admin", "/report", "список пользователей с номерами (по номеру тоже можно банить/мутить)"),
    ("admin", "/rank moder @user", "выдать ранг модератора"),
    ("owner", "/rank admin @user", "выдать ранг админа"),
    ("owner", "/people list", "полный список всех пользователей чата"),
]


@router.message(Command("help"))
async def cmd_help(message: Message):
    chat_id = message.chat.id
    # смотрим ранг того кто спрашивает - по нему решаем что показывать
    caller_rank = get_rank(chat_id, message.from_user.id)
    caller_level = rank_level(caller_rank)

    lines = [f"Ваш ранг: {RANK_TITLES.get(caller_rank, caller_rank)}", ""]
    lines.append("Доступные вам команды:")

    for min_rank, cmd, desc in COMMANDS:
        if min_rank is None or caller_level >= rank_level(min_rank):
            lines.append(f"{cmd} - {desc}")

    if not owner_exists(chat_id):
        lines.append("")
        lines.append('/rank owner @user - стать владельцем чата (сработает только 1 раз)')

    await message.answer("\n".join(lines))
