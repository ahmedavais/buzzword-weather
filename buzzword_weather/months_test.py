from datetime import date, datetime, timezone

from buzzword_weather.months import Month, complete_months_before, months_ending


def test_counts_back_from_the_month_of_the_given_day():
    assert months_ending(date(2026, 3, 15), count=3) == [Month(2026, 1), Month(2026, 2), Month(2026, 3)]


def test_crosses_into_the_previous_year():
    assert months_ending(date(2026, 1, 31), count=2) == [Month(2025, 12), Month(2026, 1)]


def test_a_month_spans_from_its_first_moment_to_the_next_month_in_utc():
    december = Month(2025, 12)

    assert december.starts_at == int(datetime(2025, 12, 1, tzinfo=timezone.utc).timestamp())
    assert december.ends_at == int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp())


def test_reads_as_a_short_label():
    assert Month(2026, 3).label == "Mar 2026"


def test_complete_months_stop_before_the_month_still_in_progress():
    assert complete_months_before(date(2026, 10, 12), count=2) == [Month(2026, 8), Month(2026, 9)]
