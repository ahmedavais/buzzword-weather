from buzzword_weather.almanac import Almanac
from buzzword_weather.barometer import Barometer
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Month

AUGUST, SEPTEMBER = Month(2026, 8), Month(2026, 9)


def test_reads_recorded_counts_without_searching():
    hacker_news = HackerNews.create_null(mentions=999)
    searches = hacker_news.track_searches()
    almanac = Almanac().with_record("agile", AUGUST, 90).with_record("agile", SEPTEMBER, 96)

    counts = Barometer(almanac, hacker_news).mentions("agile", [AUGUST, SEPTEMBER])

    assert counts == [90, 96]
    assert searches.data == []


def test_searches_only_the_periods_the_almanac_lacks():
    hacker_news = HackerNews.create_null(mentions=7)
    searches = hacker_news.track_searches()
    almanac = Almanac().with_record("agile", AUGUST, 90)

    counts = Barometer(almanac, hacker_news).mentions("agile", [AUGUST, SEPTEMBER])

    assert counts == [90, 7]
    assert searches.data == [{"term": "agile", "period": SEPTEMBER}]


def test_searches_everything_for_a_buzzword_nobody_recorded():
    hacker_news = HackerNews.create_null(mentions=3)
    searches = hacker_news.track_searches()

    counts = Barometer(Almanac(), hacker_news).mentions("evals", [AUGUST, SEPTEMBER])

    assert counts == [3, 3]
    assert len(searches.data) == 2
