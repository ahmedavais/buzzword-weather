from datetime import UTC, date, datetime

from buzzword_weather.periods import (
    Month,
    Quarter,
    Week,
    complete_months_before,
    complete_quarters_before,
    complete_quarters_since,
    edge_months,
    finished_weeks_before,
    months_ending,
)


def test_counts_back_from_the_month_of_the_given_day():
    assert months_ending(date(2026, 3, 15), count=3) == [Month(2026, 1), Month(2026, 2), Month(2026, 3)]


def test_crosses_into_the_previous_year():
    assert months_ending(date(2026, 1, 31), count=2) == [Month(2025, 12), Month(2026, 1)]


def test_a_month_spans_from_its_first_moment_to_the_next_month_in_utc():
    december = Month(2025, 12)

    assert december.starts_at == int(datetime(2025, 12, 1, tzinfo=UTC).timestamp())
    assert december.ends_at == int(datetime(2026, 1, 1, tzinfo=UTC).timestamp())


def test_reads_as_a_short_label():
    assert Month(2026, 3).label == "Mar 2026"


def test_complete_months_stop_before_the_month_still_in_progress():
    assert complete_months_before(date(2026, 10, 12), count=2) == [Month(2026, 8), Month(2026, 9)]


def test_a_quarter_spans_its_three_months():
    third = Quarter(2026, 3)

    assert third.starts_at == Month(2026, 7).starts_at
    assert third.ends_at == Month(2026, 10).starts_at
    assert third.label == "Q3 2026"


def test_the_last_quarter_ends_at_the_new_year():
    assert Quarter(2025, 4).ends_at == Month(2026, 1).starts_at


def test_complete_quarters_stop_before_the_quarter_still_in_progress():
    assert complete_quarters_before(date(2026, 10, 12), count=3) == [Quarter(2026, 1), Quarter(2026, 2), Quarter(2026, 3)]


def test_complete_quarters_since_a_year_start_with_its_first_quarter():
    quarters = complete_quarters_since(2007, before=date(2026, 10, 12))

    assert quarters[0] == Quarter(2007, 1)
    assert quarters[-1] == Quarter(2026, 3)
    assert len(quarters) == 79


def test_keys_a_month_and_a_quarter_so_they_can_be_recorded():
    assert (Month(2026, 9).key, Quarter(2026, 3).key) == ("2026-09", "2026-Q3")


def test_knows_the_months_that_begin_and_end_each_period():
    assert edge_months([Month(2026, 8), Month(2026, 9), Quarter(2026, 3)]) == [
        Month(2026, 7),
        Month(2026, 8),
        Month(2026, 9),
        Month(2026, 10),
    ]


def test_a_week_runs_from_monday_midnight_to_the_next_monday_in_utc():
    week = Week(2026, 44)

    assert week.starts_at == int(datetime(2026, 10, 26, tzinfo=UTC).timestamp())
    assert week.ends_at == int(datetime(2026, 11, 2, tzinfo=UTC).timestamp())


def test_a_week_reads_as_its_monday_to_its_sunday():
    assert Week(2026, 44).label == "26 Oct to 1 Nov 2026"


def test_a_week_keys_by_its_iso_number_and_back():
    assert Week(2026, 2).key == "2026-W02"
    assert Week.from_key("2026-W02") == Week(2026, 2)


def test_weeks_cross_into_the_next_iso_year():
    assert Week(2026, 53).next() == Week(2027, 1)
    assert Week(2027, 1).previous() == Week(2026, 53)


def test_a_monday_run_finishes_with_the_week_that_just_ended():
    assert finished_weeks_before(date(2026, 11, 2), count=2) == [Week(2026, 43), Week(2026, 44)]


def test_a_sunday_run_leaves_out_the_week_still_in_progress():
    assert finished_weeks_before(date(2026, 11, 1), count=1) == [Week(2026, 43)]
