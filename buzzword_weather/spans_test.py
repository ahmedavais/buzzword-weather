from datetime import date

from buzzword_weather.periods import Month, Quarter
from buzzword_weather.spans import Span

TODAY = date(2026, 10, 12)


def test_shows_the_last_two_years_month_by_month():
    periods = Span.LAST_2_YEARS.periods_before(TODAY)

    assert (len(periods), periods[0], periods[-1]) == (24, Month(2024, 10), Month(2026, 9))


def test_shows_the_last_ten_years_quarter_by_quarter():
    periods = Span.LAST_10_YEARS.periods_before(TODAY)

    assert (len(periods), periods[0], periods[-1]) == (40, Quarter(2016, 4), Quarter(2026, 3))


def test_shows_everything_since_hacker_news_began_quarter_by_quarter():
    periods = Span.ALL_TIME.periods_before(TODAY)

    assert (periods[0], periods[-1]) == (Quarter(2007, 1), Quarter(2026, 3))


def test_reads_as_a_choice_a_visitor_can_make():
    assert [span.label for span in Span] == ["Last 2 years", "Last 10 years", "All time"]


def test_names_the_step_between_points():
    assert [span.step for span in Span] == ["month", "quarter", "quarter"]
