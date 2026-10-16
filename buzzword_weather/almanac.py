import json
import re

from buzzword_weather.periods import Month, Period

MONTH_KEY = re.compile(r"^(\d{4})-(\d{2})$")


class Almanac:
    @staticmethod
    def from_json(text: str) -> "Almanac":
        recorded = json.loads(text)
        return Almanac(recorded["mentions"], recorded["items_posted_before"])

    def __init__(self, mentions: dict[str, dict[str, int]] | None = None, items_posted: dict[str, int] | None = None):
        self._mentions = mentions or {}
        self._items_posted = items_posted or {}

    def recorded(self, phrase: str, period: Period) -> int | None:
        return self._mentions.get(phrase, {}).get(period.key)

    def with_record(self, phrase: str, period: Period, count: int) -> "Almanac":
        mentions = {known: dict(counts) for known, counts in self._mentions.items()}
        mentions.setdefault(phrase, {})[period.key] = count
        return Almanac(mentions, self._items_posted)

    def items_posted_before(self, month: Month) -> int | None:
        return self._items_posted.get(month.key)

    def with_items_posted_before(self, month: Month, count: int) -> "Almanac":
        return Almanac(self._mentions, {**self._items_posted, month.key: count})

    def latest_month(self) -> Month | None:
        months = [
            Month(int(match[1]), int(match[2]))
            for counts in self._mentions.values()
            for key in counts
            if (match := MONTH_KEY.match(key))
        ]
        return max(months, key=lambda month: (month.year, month.month), default=None)

    def gaps(self, phrases: list[str], periods: list[Period]) -> dict[str, list[Period]]:
        missing = {phrase: [period for period in periods if self.recorded(phrase, period) is None] for phrase in phrases}
        return {phrase: lacking for phrase, lacking in missing.items() if lacking}

    def months_lacking_items_posted(self, months: list[Month]) -> list[Month]:
        return [month for month in months if self.items_posted_before(month) is None]

    def to_json(self) -> str:
        return json.dumps({"mentions": self._mentions, "items_posted_before": self._items_posted}, indent=1, sort_keys=True)
