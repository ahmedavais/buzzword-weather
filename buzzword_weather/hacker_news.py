import json
from typing import Any

from buzzword_weather.http_client import HttpClient
from buzzword_weather.output_tracker import OutputListener, OutputTracker
from buzzword_weather.periods import Month, Period

SEARCH_URL = "https://hn.algolia.com/api/v1/search"
BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"


class HackerNews:
    @staticmethod
    def create() -> "HackerNews":
        return HackerNews(HttpClient.create())

    @staticmethod
    def create_null(mentions: int | list[int] = 0, items_posted: int = 0) -> "HackerNews":
        mention_counts = [_mention_count(count) for count in mentions] if isinstance(mentions, list) else _mention_count(mentions)
        return HackerNews(HttpClient.create_null(bodies={SEARCH_URL: mention_counts, BY_DATE_URL: _newest_item(items_posted)}))

    def __init__(self, http: HttpClient):
        self._http = http
        self._searches: OutputListener[dict[str, Any]] = OutputListener()
        self._item_lookups: OutputListener[Month] = OutputListener()

    def track_searches(self) -> OutputTracker[dict[str, Any]]:
        return self._searches.track()

    def track_item_lookups(self) -> OutputTracker[Month]:
        return self._item_lookups.track()

    def mentions_by_period(self, term: str, periods: list[Period]) -> list[int]:
        return [self.mentions(term, period) for period in periods]

    def mentions(self, term: str, period: Period) -> int:
        self._searches.emit({"term": term, "period": period})
        answer = self._http.get_json(SEARCH_URL, _search_for(term, period))
        count = answer.get("nbHits") if isinstance(answer, dict) else None
        if not isinstance(count, int):
            raise ValueError(f"Hacker News gave no mention count for {term!r} in {period.label}: {json.dumps(answer)[:200]}")
        return count

    def items_posted_before(self, month: Month) -> int:
        self._item_lookups.emit(month)
        answer = self._http.get_json(BY_DATE_URL, {"numericFilters": f"created_at_i<{month.starts_at}", "hitsPerPage": 1})
        hits = answer.get("hits") if isinstance(answer, dict) else None
        if not hits:
            raise ValueError(f"Hacker News gave no newest item from before {month.label}: {json.dumps(answer)[:200]}")
        return int(hits[0]["objectID"])


def _search_for(term: str, period: Period) -> dict[str, Any]:
    return {
        "query": f'"{term}"',
        "tags": "(story,comment)",
        "numericFilters": f"created_at_i>={period.starts_at},created_at_i<{period.ends_at}",
        "hitsPerPage": 0,
    }


def _mention_count(count: int) -> str:
    return json.dumps({"nbHits": count})


def _newest_item(items_posted: int) -> str:
    return json.dumps({"hits": [{"objectID": str(items_posted)}]})
