import json
from typing import Any

from buzzword_weather.http_client import HttpClient
from buzzword_weather.months import Month
from buzzword_weather.output_tracker import OutputListener, OutputTracker

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

    def mentions_by_month(self, term: str, months: list[Month]) -> list[int]:
        return [self.mentions(term, month) for month in months]

    def mentions(self, term: str, month: Month) -> int:
        self._searches.emit({"term": term, "month": month})
        answer = self._http.get_json(SEARCH_URL, _search_for(term, month))
        count = answer.get("nbHits") if isinstance(answer, dict) else None
        if not isinstance(count, int):
            raise ValueError(f"Hacker News gave no mention count for {term!r} in {month.label}: {json.dumps(answer)[:200]}")
        return count


def _search_for(term: str, month: Month) -> dict[str, Any]:
    return {
        "query": f'"{term}"',
        "tags": "(story,comment)",
        "numericFilters": f"created_at_i>={month.starts_at},created_at_i<{month.ends_at}",
        "hitsPerPage": 0,
    }


def _answer(count: int) -> str:
    return json.dumps({"nbHits": count})
