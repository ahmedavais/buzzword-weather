from buzzword_weather.almanac import Almanac
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Month
from buzzword_weather.recorder import record_missing

AUGUST, SEPTEMBER = Month(2026, 8), Month(2026, 9)


def test_records_the_counts_the_almanac_lacks():
    almanac = record_missing(Almanac(), HackerNews.create_null(mentions=[12, 15]), ["agile"], [AUGUST, SEPTEMBER], pause=lambda: None)

    assert [almanac.recorded("agile", period) for period in (AUGUST, SEPTEMBER)] == [12, 15]


def test_leaves_recorded_counts_alone_and_does_not_search_for_them():
    hacker_news = HackerNews.create_null(mentions=15)
    searches = hacker_news.track_searches()

    almanac = record_missing(Almanac().with_record("agile", AUGUST, 12), hacker_news, ["agile"], [AUGUST, SEPTEMBER], pause=lambda: None)

    assert almanac.recorded("agile", AUGUST) == 12
    assert searches.data == [{"term": "agile", "period": SEPTEMBER}]


def test_pauses_after_every_search():
    pauses = []

    record_missing(Almanac(), HackerNews.create_null(), ["agile", "scrum"], [SEPTEMBER], pause=lambda: pauses.append("paused"))

    assert pauses == ["paused", "paused"]
