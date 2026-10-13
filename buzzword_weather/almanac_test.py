from buzzword_weather.almanac import Almanac
from buzzword_weather.periods import Month, Quarter


def test_remembers_a_recorded_count():
    almanac = Almanac().with_record("vibe coding", Month(2026, 9), 425)

    assert almanac.recorded("vibe coding", Month(2026, 9)) == 425


def test_knows_nothing_it_was_not_told():
    almanac = Almanac().with_record("vibe coding", Month(2026, 9), 425)

    assert almanac.recorded("vibe coding", Month(2026, 8)) is None
    assert almanac.recorded("agile", Month(2026, 9)) is None


def test_tells_a_month_from_the_quarter_it_starts():
    almanac = Almanac().with_record("agile", Quarter(2026, 3), 299)

    assert almanac.recorded("agile", Month(2026, 7)) is None


def test_survives_a_round_trip_through_json():
    almanac = Almanac().with_record("agile", Quarter(2026, 3), 299).with_record("agile", Month(2026, 9), 96)

    restored = Almanac.from_json(almanac.to_json())

    assert restored.recorded("agile", Quarter(2026, 3)) == 299
    assert restored.recorded("agile", Month(2026, 9)) == 96
