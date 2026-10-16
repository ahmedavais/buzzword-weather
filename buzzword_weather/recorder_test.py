from buzzword_weather.almanac import Almanac
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Month
from buzzword_weather.recorder import record_missing

AUGUST, SEPTEMBER, OCTOBER = Month(2026, 8), Month(2026, 9), Month(2026, 10)


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

    almanac = Almanac().with_items_posted_before(SEPTEMBER, 45_000_000).with_items_posted_before(OCTOBER, 45_300_000)

    record_missing(almanac, HackerNews.create_null(), ["agile", "scrum"], [SEPTEMBER], pause=lambda: pauses.append("paused"))

    assert pauses == ["paused", "paused"]


def test_records_the_items_posted_before_each_month_at_the_edge_of_a_period():
    almanac = record_missing(Almanac(), HackerNews.create_null(items_posted=45_000_000), [], [AUGUST, SEPTEMBER], pause=lambda: None)

    assert [almanac.items_posted_before(month) for month in (AUGUST, SEPTEMBER, OCTOBER)] == [45_000_000] * 3


def test_leaves_recorded_items_posted_alone_and_does_not_look_them_up():
    hacker_news = HackerNews.create_null(items_posted=45_000_000)
    lookups = hacker_news.track_item_lookups()

    almanac = record_missing(Almanac().with_items_posted_before(AUGUST, 44_000_000), hacker_news, [], [AUGUST], pause=lambda: None)

    assert almanac.items_posted_before(AUGUST) == 44_000_000
    assert lookups.data == [SEPTEMBER]


def test_pauses_after_every_lookup_of_items_posted():
    pauses = []

    record_missing(Almanac(), HackerNews.create_null(), [], [SEPTEMBER], pause=lambda: pauses.append("paused"))

    assert pauses == ["paused", "paused"]
