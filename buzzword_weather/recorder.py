from typing import Callable

from buzzword_weather.almanac import Almanac
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Period


def record_missing(almanac: Almanac, hacker_news: HackerNews, phrases: list[str], periods: list[Period], pause: Callable[[], None]) -> Almanac:
    for phrase in phrases:
        for period in periods:
            if almanac.recorded(phrase, period) is None:
                almanac = almanac.with_record(phrase, period, hacker_news.mentions(phrase, period))
                pause()
    return almanac
