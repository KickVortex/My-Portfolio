from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import get_rank
from roles import rank_level
from report_cache import save_report
from handlers.report import build_user_list

router = Router()


@router.message(Command("people"))
async def cmd_people(message: Message):
    args = message.text.split()
    if len(args) < 2 or args[1].lower() != "list":
        await message.answer("Используйте: /people list")
        return

    chat_id = message.chat.id
    caller_rank = get_rank(chat_id, message.from_user.id)

    if rank_level(caller_rank) < rank_level("owner"):
        await message.answer("Эта команда доступна только владельцу")
        return

    lines, ordered = build_user_list(chat_id)
    if not lines:
        await message.answer("Пока никого не видел в этом чате")
        return

    # этим же номерам можно пользоваться в /ban, /mute и т.д.
    save_report(chat_id, ordered)

    text = f"Всего в базе: {len(lines)} чел.\n\n" + "\n".join(lines)
    await message.answer(text)
