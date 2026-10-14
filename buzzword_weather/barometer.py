from concurrent.futures import ThreadPoolExecutor

from buzzword_weather.almanac import Almanac
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Period

PARALLEL_SEARCHES = 4


class Barometer:
    def __init__(self, almanac: Almanac, hacker_news: HackerNews):
        self._almanac = almanac
        self._hacker_news = hacker_news

    def mentions(self, phrase: str, periods: list[Period]) -> list[int]:
        recorded = {period: self._almanac.recorded(phrase, period) for period in periods}
        missing = [period for period, count in recorded.items() if count is None]
        with ThreadPoolExecutor(max_workers=PARALLEL_SEARCHES) as pool:
            searched = dict(zip(missing, pool.map(lambda period: self._hacker_news.mentions(phrase, period), missing)))
        return [recorded[period] if recorded[period] is not None else searched[period] for period in periods]
