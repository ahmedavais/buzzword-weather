import json

from buzzword_weather.periods import Period


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

    def to_json(self) -> str:
        return json.dumps(self._records, indent=1, sort_keys=True)
