from buzzword_weather.almanac import Almanac
from buzzword_weather.barometer import Barometer
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Month

AUGUST, SEPTEMBER, OCTOBER = Month(2026, 8), Month(2026, 9), Month(2026, 10)


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


def test_gives_mentions_per_10000_posts_from_the_almanac_alone():
    hacker_news = HackerNews.create_null(mentions=999, items_posted=999)
    searches, lookups = hacker_news.track_searches(), hacker_news.track_item_lookups()
    almanac = (
        Almanac()
        .with_record("agile", AUGUST, 90)
        .with_record("agile", SEPTEMBER, 96)
        .with_items_posted_before(AUGUST, 45_000_000)
        .with_items_posted_before(SEPTEMBER, 45_300_000)
        .with_items_posted_before(OCTOBER, 45_620_000)
    )

    rates = Barometer(almanac, hacker_news).mention_rates("agile", [AUGUST, SEPTEMBER])

    assert rates == [3.0, 3.0]
    assert (searches.data, lookups.data) == ([], [])


def test_looks_up_only_the_items_posted_the_almanac_lacks():
    hacker_news = HackerNews.create_null(items_posted=45_620_000)
    lookups = hacker_news.track_item_lookups()
    almanac = Almanac().with_record("agile", SEPTEMBER, 96).with_items_posted_before(SEPTEMBER, 45_300_000)

    rates = Barometer(almanac, hacker_news).mention_rates("agile", [SEPTEMBER])

    assert rates == [3.0]
    assert lookups.data == [OCTOBER]
