import json
from typing import Any

from buzzword_weather.http_client import HttpClient
from buzzword_weather.output_tracker import OutputListener, OutputTracker
from buzzword_weather.periods import Period

SEARCH_URL = "https://hn.algolia.com/api/v1/search"


class HackerNews:
    @staticmethod
    def create() -> "HackerNews":
        return HackerNews(HttpClient.create())

    @staticmethod
    def create_null(mentions: int | list[int] = 0) -> "HackerNews":
        bodies = [_answer(count) for count in mentions] if isinstance(mentions, list) else _answer(mentions)
        return HackerNews(HttpClient.create_null(bodies=bodies))

    def __init__(self, http: HttpClient):
        self._http = http
        self._searches: OutputListener[dict[str, Any]] = OutputListener()

    def track_searches(self) -> OutputTracker[dict[str, Any]]:
        return self._searches.track()

    def mentions_by_period(self, term: str, periods: list[Period]) -> list[int]:
        return [self.mentions(term, period) for period in periods]

    def mentions(self, term: str, period: Period) -> int:
        self._searches.emit({"term": term, "period": period})
        answer = self._http.get_json(SEARCH_URL, _search_for(term, period))
        count = answer.get("nbHits") if isinstance(answer, dict) else None
        if not isinstance(count, int):
            raise ValueError(f"Hacker News gave no mention count for {term!r} in {period.label}: {json.dumps(answer)[:200]}")
        return count


def _search_for(term: str, period: Period) -> dict[str, Any]:
    return {
        "query": f'"{term}"',
        "tags": "(story,comment)",
        "numericFilters": f"created_at_i>={period.starts_at},created_at_i<{period.ends_at}",
        "hitsPerPage": 0,
    }


def _answer(count: int) -> str:
    return json.dumps({"nbHits": count})
