from datetime import date
from pathlib import Path

from buzzword_weather.almanac import Almanac
from buzzword_weather.catalog import CATALOG
from buzzword_weather.periods import Month, Period, complete_quarters_since, edge_months, months_ending
from buzzword_weather.spans import HACKER_NEWS_FIRST_YEAR

ALMANAC = Almanac.from_json((Path(__file__).parent.parent / "almanac.json").read_text())
MOST_MONTHS_BEHIND = 2


def periods_through(month: Month) -> list[Period]:
    following = month.next()
    return months_ending(date(month.year, month.month, 1), 24) + complete_quarters_since(
        HACKER_NEWS_FIRST_YEAR, before=date(following.year, following.month, 1)
    )


def months_between(earlier: Month, later: Month) -> int:
    return (later.year - earlier.year) * 12 + later.month - earlier.month


def test_records_every_catalog_buzzword_for_every_period_up_to_its_latest_month():
    latest = ALMANAC.latest_month()
    assert latest is not None, "The almanac is empty"

    gaps = ALMANAC.gaps([buzzword.phrase for buzzword in CATALOG], periods_through(latest))

    assert gaps == {}, f"The almanac lacks counts through {latest.label}: " + ", ".join(
        f"{phrase} ({len(lacking)} periods)" for phrase, lacking in gaps.items()
    )


def test_records_the_items_posted_at_every_edge_of_those_periods():
    latest = ALMANAC.latest_month()
    assert latest is not None, "The almanac is empty"

    lacking = ALMANAC.months_lacking_items_posted(edge_months(periods_through(latest)))

    assert lacking == [], f"The almanac lacks how many items were posted before {len(lacking)} months: " + ", ".join(
        month.label for month in lacking[:5]
    )


def test_was_refreshed_recently():
    latest = ALMANAC.latest_month()
    this_month = Month(date.today().year, date.today().month)

    assert latest is not None and months_between(latest, this_month) <= MOST_MONTHS_BEHIND, (
        f"The almanac stops at {latest.label if latest else 'nothing'}; the monthly refresh may have stopped"
    )
