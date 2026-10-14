import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from buzzword_weather.configurable_responses import ConfigurableResponses
from buzzword_weather.output_tracker import OutputListener, OutputTracker

NULLED_BODY = '{"nulled": "Nulled HttpClient default body"}'
USER_AGENT = "buzzword-weather (https://github.com/ahmedavais/buzzword-weather)"
TIMEOUT_SECONDS = 15
SLOW_DOWN_STATUSES = {403, 429}
TRIES = 4
FIRST_PAUSE_SECONDS = 1.0


@dataclass(frozen=True)
class Answer:
    status: int
    body: str


class Fetcher(Protocol):
    def fetch(self, url: str) -> Answer: ...


class HttpClient:
    @staticmethod
    def create() -> "HttpClient":
        return HttpClient(_UrllibFetcher(), time.sleep)

    @staticmethod
    def create_null(bodies: str | Answer | list[str | Answer] = NULLED_BODY) -> "HttpClient":
        return HttpClient(_StubbedFetcher(bodies), lambda seconds: None)

    def __init__(self, fetcher: Fetcher, pause: Callable[[float], None]):
        self._fetcher = fetcher
        self._pause = pause
        self._requests: OutputListener[dict[str, Any]] = OutputListener()
        self._pauses: OutputListener[float] = OutputListener()

    def track_requests(self) -> OutputTracker[dict[str, Any]]:
        return self._requests.track()

    def track_pauses(self) -> OutputTracker[float]:
        return self._pauses.track()

    def get_json(self, url: str, params: dict[str, Any]) -> Any:
        self._requests.emit({"url": url, "params": params})
        answer = self._fetch_patiently(url, f"{url}?{urllib.parse.urlencode(params)}")
        try:
            return json.loads(answer.body)
        except json.JSONDecodeError as error:
            raise ValueError(f"GET {url} answered with a body that is not JSON: {answer.body[:200]}") from error

    def _fetch_patiently(self, url: str, full_url: str) -> Answer:
        pause_seconds = FIRST_PAUSE_SECONDS
        for attempt in range(1, TRIES + 1):
            answer = self._fetcher.fetch(full_url)
            if answer.status not in SLOW_DOWN_STATUSES:
                break
            if attempt == TRIES:
                raise ValueError(f"GET {url} was refused with {answer.status} after {TRIES} tries: {answer.body[:200]}")
            self._pauses.emit(pause_seconds)
            self._pause(pause_seconds)
            pause_seconds *= 2
        if answer.status != 200:
            raise ValueError(f"GET {url} answered {answer.status}: {answer.body[:200]}")
        return answer


class _UrllibFetcher:
    def fetch(self, url: str) -> Answer:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return Answer(response.status, response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            return Answer(error.code, error.read().decode("utf-8", errors="replace"))


class _StubbedFetcher:
    def __init__(self, bodies: str | Answer | list[str | Answer]):
        self._answers = ConfigurableResponses(bodies, "the nulled HttpClient")

    def fetch(self, url: str) -> Answer:
        answer = self._answers.next()
        return answer if isinstance(answer, Answer) else Answer(200, answer)
