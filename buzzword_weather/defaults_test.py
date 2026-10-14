from buzzword_weather.defaults import pick_defaults
from buzzword_weather.forecast import Weather

OVERHEAD, PASSING, CLEARING, BREEZE = (
    Weather.STORM_OVERHEAD,
    Weather.STORM_PASSING,
    Weather.CLEARING_SKIES,
    Weather.STEADY_BREEZE,
)


def test_picks_in_pool_order_when_the_weather_varies():
    assert pick_defaults([("a", OVERHEAD), ("b", PASSING), ("c", CLEARING)], most=3) == ["a", "b", "c"]


def test_skips_a_third_buzzword_in_the_same_weather():
    pool = [("a", PASSING), ("b", PASSING), ("c", PASSING), ("d", BREEZE)]

    assert pick_defaults(pool, most=3) == ["a", "b", "d"]


def test_fills_from_the_skipped_in_pool_order_when_the_pool_lacks_variety():
    pool = [("a", PASSING), ("b", PASSING), ("c", PASSING), ("d", PASSING)]

    assert pick_defaults(pool, most=3) == ["a", "b", "c"]


def test_keeps_the_pool_order_in_what_it_shows():
    pool = [("a", PASSING), ("b", PASSING), ("c", PASSING), ("d", BREEZE), ("e", PASSING)]

    assert pick_defaults(pool, most=4) == ["a", "b", "c", "d"]


def test_never_picks_more_than_asked():
    pool = [(name, weather) for name, weather in zip("abcdefghij", [OVERHEAD, PASSING, CLEARING, BREEZE] * 3, strict=False)]

    assert len(pick_defaults(pool, most=7)) == 7
