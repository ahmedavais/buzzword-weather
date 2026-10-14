import json
import re

from buzzword_weather.periods import Month, Period

MONTH_KEY = re.compile(r"^(\d{4})-(\d{2})$")


class Almanac:
    @staticmethod
    def from_json(text: str) -> "Almanac":
        return Almanac(json.loads(text))

    def __init__(self, records: dict[str, dict[str, int]] | None = None):
        self._records = records or {}

    def recorded(self, phrase: str, period: Period) -> int | None:
        return self._records.get(phrase, {}).get(period.key)

    def with_record(self, phrase: str, period: Period, count: int) -> "Almanac":
        records = {known: dict(counts) for known, counts in self._records.items()}
        records.setdefault(phrase, {})[period.key] = count
        return Almanac(records)

    def latest_month(self) -> Month | None:
        months = [
            Month(int(match[1]), int(match[2]))
            for counts in self._records.values()
            for key in counts
            if (match := MONTH_KEY.match(key))
        ]
        return max(months, key=lambda month: (month.year, month.month), default=None)

    def gaps(self, phrases: list[str], periods: list[Period]) -> dict[str, list[Period]]:
        missing = {phrase: [period for period in periods if self.recorded(phrase, period) is None] for phrase in phrases}
        return {phrase: lacking for phrase, lacking in missing.items() if lacking}

    def to_json(self) -> str:
        return json.dumps(self._records, indent=1, sort_keys=True)
