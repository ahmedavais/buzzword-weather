import json
from dataclasses import dataclass, field, replace

from buzzword_weather.periods import Week

WEEKS_KEPT = 13

Example = tuple[int, str]


@dataclass(frozen=True)
class WeekOfWords:
    titles: int
    stories: dict[str, int]
    risers: dict[str, list[Example]] = field(default_factory=dict)

    def rate(self, term: str) -> float:
        return self.stories.get(term, 0) / self.titles * 10_000 if self.titles else 0.0


@dataclass(frozen=True)
class WeeklyWords:
    weeks: dict[Week, WeekOfWords] = field(default_factory=dict)

    @staticmethod
    def from_json(text: str) -> "WeeklyWords":
        stored = json.loads(text).get("weeks", {})
        return WeeklyWords({Week.from_key(key): _week_from(entry) for key, entry in stored.items()})

    def to_json(self) -> str:
        weeks = {week.key: _entry_of(self.weeks[week]) for week in self.recorded_weeks()}
        return json.dumps({"weeks": weeks}, indent=1, ensure_ascii=False) + "\n"

    def recorded_weeks(self) -> list[Week]:
        return sorted(self.weeks, key=lambda week: week.starts_at)

    def latest(self) -> Week | None:
        recorded = self.recorded_weeks()
        return recorded[-1] if recorded else None

    def before(self, week: Week, count: int) -> list[WeekOfWords]:
        return [self.weeks[earlier] for earlier in self.recorded_weeks() if earlier.starts_at < week.starts_at][-count:]

    def with_week(self, week: Week, words: WeekOfWords) -> "WeeklyWords":
        kept = sorted({**self.weeks, week: words}.items(), key=lambda item: item[0].starts_at)[-WEEKS_KEPT:]
        return replace(self, weeks=dict(kept))


def _week_from(entry: dict) -> WeekOfWords:
    risers = {term: [(int(story_id), title) for story_id, title in examples] for term, examples in entry.get("risers", {}).items()}
    return WeekOfWords(int(entry["titles"]), {term: int(count) for term, count in entry["stories"].items()}, risers)


def _entry_of(words: WeekOfWords) -> dict:
    stories = dict(sorted(words.stories.items(), key=lambda item: (-item[1], item[0])))
    return {"titles": words.titles, "risers": {term: [list(example) for example in examples] for term, examples in words.risers.items()}, "stories": stories}
