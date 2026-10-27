from datetime import date
from pathlib import Path

import pytest

from buzzword_weather.periods import finished_weeks_before
from buzzword_weather.titles import STOPWORDS
from buzzword_weather.weekly_words import WeeklyWords

RECORD = WeeklyWords.from_json((Path(__file__).parent.parent / "weekly_words.json").read_text())
MOST_WEEKS_BEHIND = 2
FEWEST_TITLES = 2000

pytestmark = pytest.mark.skipif(RECORD.latest() is None, reason="The weekly words are not backfilled yet")


def test_was_recorded_recently():
    expected = finished_weeks_before(date.today(), count=MOST_WEEKS_BEHIND)[0]

    assert RECORD.latest().starts_at >= expected.starts_at, (
        f"The weekly words stop at {RECORD.latest().label}; the weekly recording may have stopped"
    )


def test_counts_a_plausible_number_of_titles_every_week():
    thin = [week.label for week in RECORD.recorded_weeks() if RECORD.weeks[week].titles < FEWEST_TITLES]

    assert thin == [], f"Too few story titles were recorded for {', '.join(thin)}; the fetch may be losing stories"


def test_never_ranks_a_common_word_or_a_number():
    junk = [
        term
        for week in RECORD.recorded_weeks()
        for term in RECORD.weeks[week].risers
        if any(word in STOPWORDS or word.isdigit() for word in term.split(" "))
    ]

    assert junk == []
