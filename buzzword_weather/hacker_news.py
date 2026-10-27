import json
from dataclasses import dataclass
from typing import Any

from buzzword_weather.http_client import HttpClient
from buzzword_weather.output_tracker import OutputListener, OutputTracker
from buzzword_weather.periods import Month, Period

SEARCH_URL = "https://hn.algolia.com/api/v1/search"
BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"
SLICE_SECONDS = 6 * 60 * 60
MOST_HITS = 1000


@dataclass(frozen=True)
class Story:
    id: int
    title: str
    url: str | None = None


class HackerNews:
    @staticmethod
    def create() -> "HackerNews":
        return HackerNews(HttpClient.create())

    @staticmethod
    def create_null(mentions: int | list[int] = 0, items_posted: int = 0, stories: list[Story] | None = None) -> "HackerNews":
        mention_counts = [_mention_count(count) for count in mentions] if isinstance(mentions, list) else _mention_count(mentions)
        by_date = _stories_found(stories) if stories is not None else _newest_item(items_posted)
        return HackerNews(HttpClient.create_null(bodies={SEARCH_URL: mention_counts, BY_DATE_URL: by_date}))

    def __init__(self, http: HttpClient):
        self._http = http
        self._searches: OutputListener[dict[str, Any]] = OutputListener()
        self._item_lookups: OutputListener[Month] = OutputListener()
        self._story_slices: OutputListener[tuple[int, int]] = OutputListener()

    def track_searches(self) -> OutputTracker[dict[str, Any]]:
        return self._searches.track()

    def track_item_lookups(self) -> OutputTracker[Month]:
        return self._item_lookups.track()

    def track_story_slices(self) -> OutputTracker[tuple[int, int]]:
        return self._story_slices.track()

    def stories(self, starts_at: int, ends_at: int) -> list[Story]:
        found: dict[int, Story] = {}
        for slice_start in range(starts_at, ends_at, SLICE_SECONDS):
            found |= {story.id: story for story in self._stories_in_slice(slice_start, min(slice_start + SLICE_SECONDS, ends_at))}
        return sorted(found.values(), key=lambda story: story.id)

    def _stories_in_slice(self, starts_at: int, ends_at: int) -> list[Story]:
        self._story_slices.emit((starts_at, ends_at))
        answer = self._http.get_json(BY_DATE_URL, _stories_between(starts_at, ends_at))
        hits = answer.get("hits") if isinstance(answer, dict) else None
        if not isinstance(hits, list) or not isinstance(answer.get("nbHits"), int):
            raise ValueError(f"Hacker News gave no stories between {starts_at} and {ends_at}: {json.dumps(answer)[:200]}")
        if answer["nbHits"] <= len(hits):
            return [_story(hit) for hit in hits if "title" in hit]
        if ends_at - starts_at < 2:
            raise ValueError(f"Hacker News has more than {MOST_HITS} stories in the second starting {starts_at}")
        middle = (starts_at + ends_at) // 2
        return self._stories_in_slice(starts_at, middle) + self._stories_in_slice(middle, ends_at)

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


def _stories_between(starts_at: int, ends_at: int) -> dict[str, Any]:
    return {
        "tags": "story",
        "numericFilters": f"created_at_i>={starts_at},created_at_i<{ends_at}",
        "hitsPerPage": MOST_HITS,
        "attributesToRetrieve": "title,url",
        "attributesToHighlight": "",
    }


def _story(hit: dict[str, Any]) -> Story:
    return Story(int(hit["objectID"]), hit.get("title") or "", hit.get("url") or None)


def _stories_found(stories: list[Story]) -> str:
    hits = [{"objectID": str(story.id), "title": story.title, "url": story.url} for story in stories]
    return json.dumps({"nbHits": len(hits), "hits": hits})


def _mention_count(count: int) -> str:
    return json.dumps({"nbHits": count})


def _newest_item(items_posted: int) -> str:
    return json.dumps({"nbHits": 0, "hits": [{"objectID": str(items_posted)}]})
