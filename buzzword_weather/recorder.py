from collections.abc import Callable

from buzzword_weather.almanac import Almanac
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Period, edge_months


def record_missing(almanac: Almanac, hacker_news: HackerNews, phrases: list[str], periods: list[Period], pause: Callable[[], None]) -> Almanac:
    almanac = _record_missing_mentions(almanac, hacker_news, phrases, periods, pause)
    return _record_missing_items_posted(almanac, hacker_news, periods, pause)


def _record_missing_mentions(almanac: Almanac, hacker_news: HackerNews, phrases: list[str], periods: list[Period], pause: Callable[[], None]) -> Almanac:
    for phrase in phrases:
        for period in periods:
            if almanac.recorded(phrase, period) is None:
                almanac = almanac.with_record(phrase, period, hacker_news.mentions(phrase, period))
                pause()
    return almanac


def _record_missing_items_posted(almanac: Almanac, hacker_news: HackerNews, periods: list[Period], pause: Callable[[], None]) -> Almanac:
    for month in almanac.months_lacking_items_posted(edge_months(periods)):
        almanac = almanac.with_items_posted_before(month, hacker_news.items_posted_before(month))
        pause()
    return almanac
