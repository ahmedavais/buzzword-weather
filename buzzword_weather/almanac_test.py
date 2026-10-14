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


def test_knows_the_latest_month_it_recorded():
    almanac = Almanac().with_record("agile", Month(2026, 8), 90).with_record("scrum", Month(2026, 9), 40).with_record("agile", Quarter(2026, 3), 299)

    assert almanac.latest_month() == Month(2026, 9)


def test_has_no_latest_month_when_empty():
    assert Almanac().latest_month() is None


def test_lists_what_it_lacks_for_each_phrase():
    almanac = Almanac().with_record("agile", Month(2026, 8), 90)

    assert almanac.gaps(["agile", "scrum"], [Month(2026, 8), Month(2026, 9)]) == {
        "agile": [Month(2026, 9)],
        "scrum": [Month(2026, 8), Month(2026, 9)],
    }
