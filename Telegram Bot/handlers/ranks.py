from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import get_rank, set_rank, owner_exists
from roles import rank_level
from utils import resolve_user

router = Router()


@router.message(Command("rank"))
async def cmd_rank(message: Message):
    args = message.text.split()
    # /rank owner @username
    if len(args) < 2:
        await message.answer(
            "Используйте: /rank owner|admin|moder @username"
        )
        return

    target_rank = args[1].lower()
    username_arg = args[2] if len(args) > 2 else None

    if target_rank not in ("owner", "admin", "moder"):
        await message.answer("Ранг может быть только owner, admin или moder")
        return

    target_id = await resolve_user(message, username_arg)
    if target_id is None:
        await message.answer(
            "Не нашёл пользователя. Выберите его из списка через @, "
            "ответьте этой командой на его сообщение, или укажите номер из /report"
        )
        return

    chat_id = message.chat.id
    caller_rank = get_rank(chat_id, message.from_user.id)

    if target_rank == "owner":
        if owner_exists(chat_id):
            await message.answer("У этого чата уже есть владелец")
            return
        set_rank(chat_id, target_id, "owner")
        await message.answer("Пользователь назначен владельцем чата")
        return

    if target_rank == "admin":
        if rank_level(caller_rank) < rank_level("owner"):
            await message.answer("Назначать админов может только владелец")
            return
        set_rank(chat_id, target_id, "admin")
        await message.answer("Пользователь назначен администратором")
        return

    if target_rank == "moder":
        if rank_level(caller_rank) < rank_level("admin"):
            await message.answer("Назначать модераторов может только админ или владелец")
            return
        set_rank(chat_id, target_id, "moder")
        await message.answer("Пользователь назначен модератором")
        return
