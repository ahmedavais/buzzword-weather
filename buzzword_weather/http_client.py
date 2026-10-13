import json
import urllib.parse
import urllib.request
from typing import Any, Protocol

from buzzword_weather.configurable_responses import ConfigurableResponses
from buzzword_weather.output_tracker import OutputListener, OutputTracker

NULLED_BODY = '{"nulled": "Nulled HttpClient default body"}'
USER_AGENT = "buzzword-weather (https://github.com/ahmedavais/buzzword-weather)"
TIMEOUT_SECONDS = 15


class Fetcher(Protocol):
    def fetch(self, url: str) -> str: ...


class HttpClient:
    @staticmethod
    def create() -> "HttpClient":
        return HttpClient(_UrllibFetcher())

    @staticmethod
    def create_null(bodies: str | list[str] = NULLED_BODY) -> "HttpClient":
        return HttpClient(_StubbedFetcher(bodies))

    def __init__(self, fetcher: Fetcher):
        self._fetcher = fetcher
        self._requests: OutputListener[dict[str, Any]] = OutputListener()

    def track_requests(self) -> OutputTracker[dict[str, Any]]:
        return self._requests.track()

    def get_json(self, url: str, params: dict[str, Any]) -> Any:
        self._requests.emit({"url": url, "params": params})
        body = self._fetcher.fetch(f"{url}?{urllib.parse.urlencode(params)}")
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise ValueError(f"GET {url} answered with a body that is not JSON: {body[:200]}") from error


class _UrllibFetcher:
    def fetch(self, url: str) -> str:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")


class _StubbedFetcher:
    def __init__(self, bodies: str | list[str]):
        self._bodies = ConfigurableResponses(bodies, "the nulled HttpClient")

    def fetch(self, url: str) -> str:
        return self._bodies.next()
