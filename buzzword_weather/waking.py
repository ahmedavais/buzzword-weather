from collections.abc import Callable

TRIES = 10


def awake_within_tries(looks_awake: Callable[[], bool], reload: Callable[[], None]) -> bool:
    for attempt in range(TRIES):
        if looks_awake():
            return True
        if attempt < TRIES - 1:
            reload()
    return False
