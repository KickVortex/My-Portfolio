# иерархия рангов, чем больше число тем выше права
RANK_LEVELS = {
    "moder": 1,
    "admin": 2,
    "owner": 3,
}


def rank_level(rank: str | None) -> int:
    if rank is None:
        return 0
    return RANK_LEVELS.get(rank, 0)
