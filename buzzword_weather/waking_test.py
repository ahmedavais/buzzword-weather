from buzzword_weather.waking import TRIES, awake_within_tries


def answers(*awake: bool):
    remaining = list(awake)
    return lambda: remaining.pop(0)


def test_is_awake_at_once_without_reloading():
    reloads: list[None] = []

    assert awake_within_tries(answers(True), lambda: reloads.append(None))
    assert reloads == []


def test_reloads_until_the_app_is_awake():
    reloads: list[None] = []

    assert awake_within_tries(answers(False, False, True), lambda: reloads.append(None))
    assert len(reloads) == 2


def test_gives_up_after_its_tries():
    reloads: list[None] = []

    assert not awake_within_tries(answers(*[False] * TRIES), lambda: reloads.append(None))
    assert len(reloads) == TRIES - 1
