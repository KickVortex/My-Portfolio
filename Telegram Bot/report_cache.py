_last_report: dict[int, list[int]] = {}


def save_report(chat_id: int, user_ids: list[int]):
    _last_report[chat_id] = user_ids


def get_user_by_number(chat_id: int, number: int):
    users = _last_report.get(chat_id)
    if not users:
        return None
    if number < 1 or number > len(users):
        return None
    return users[number - 1]
