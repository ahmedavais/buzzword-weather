from concurrent.futures import ThreadPoolExecutor

from buzzword_weather.almanac import Almanac
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Month, Period

PARALLEL_SEARCHES = 4
PER_POSTS = 10_000


class Barometer:
    def __init__(self, almanac: Almanac, hacker_news: HackerNews):
        self._almanac = almanac
        self._hacker_news = hacker_news

    def mentions(self, phrase: str, periods: list[Period]) -> list[int]:
        recorded = {period: self._almanac.recorded(phrase, period) for period in periods}
        missing = [period for period, count in recorded.items() if count is None]
        with ThreadPoolExecutor(max_workers=PARALLEL_SEARCHES) as pool:
            searched = dict(zip(missing, pool.map(lambda period: self._hacker_news.mentions(phrase, period), missing), strict=True))
        return [recorded[period] if recorded[period] is not None else searched[period] for period in periods]

    def mention_rates(self, phrase: str, periods: list[Period]) -> list[float]:
        mentions = self.mentions(phrase, periods)
        return [PER_POSTS * count / self._posts_in(period) for count, period in zip(mentions, periods, strict=True)]

    def _posts_in(self, period: Period) -> int:
        return self._items_posted_before(period.next().first_month) - self._items_posted_before(period.first_month)

    def _items_posted_before(self, month: Month) -> int:
        recorded = self._almanac.items_posted_before(month)
        return recorded if recorded is not None else self._hacker_news.items_posted_before(month)
