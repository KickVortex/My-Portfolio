import sqlite3
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranks (
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rank TEXT NOT NULL,
            PRIMARY KEY (chat_id, user_id)
        )
    """)
    # кэш пользователей по чатам, чтобы можно было находить id по @username
    # и строить отчёт со списком людей. телеграм не даёт просто так получить
    # список участников чата через бота, поэтому запоминаем всех кто писал
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_cache (
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            PRIMARY KEY (chat_id, user_id)
        )
    """)
    conn.commit()
    conn.close()


def cache_user(chat_id: int, user_id: int, username: str | None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users_cache (chat_id, user_id, username)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id, user_id) DO UPDATE SET username = excluded.username
    """, (chat_id, user_id, username.lower() if username else None))
    conn.commit()
    conn.close()


def get_id_by_username(chat_id: int, username: str):
    username = username.lstrip("@").lower()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM users_cache WHERE chat_id = ? AND username = ?",
        (chat_id, username)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return row["user_id"]
    return None


def list_cached_users(chat_id: int):
    # отдаёт всех кого бот видел в этом чате, в порядке первого появления
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username FROM users_cache WHERE chat_id = ? ORDER BY rowid",
        (chat_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [(row["user_id"], row["username"]) for row in rows]


def get_rank(chat_id: int, user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT rank FROM ranks WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return row["rank"]
    return None


def set_rank(chat_id: int, user_id: int, rank: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ranks (chat_id, user_id, rank)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id, user_id) DO UPDATE SET rank = excluded.rank
    """, (chat_id, user_id, rank))
    conn.commit()
    conn.close()


def get_owner_id(chat_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM ranks WHERE chat_id = ? AND rank = 'owner'",
        (chat_id,)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return row["user_id"]
    return None


def owner_exists(chat_id: int) -> bool:
    return get_owner_id(chat_id) is not None
