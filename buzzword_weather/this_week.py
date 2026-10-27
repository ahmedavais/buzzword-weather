import re
from dataclasses import dataclass

from buzzword_weather.periods import Week
from buzzword_weather.rising import BASELINE_WEEKS, Riser, risers
from buzzword_weather.weekly_words import LEAST_STORIES, Example, WeeklyWords


@dataclass(frozen=True)
class Row:
    riser: Riser
    examples: list[Example]

    @property
    def headline(self) -> str:
        heat = self.riser.heat
        rise = f"under {LEAST_STORIES} stories a week before" if self.riser.is_new else f"{_times(self.riser.rise)} usual"
        return f"{heat.emoji} **{self.riser.term}** · {heat.value} · {rise} · {self.riser.rate:.1f} per 10,000 titles"


    @property
    def example_links(self) -> list[str]:
        return [f"[{_escaped(title)}](https://news.ycombinator.com/item?id={story_id})" for story_id, title in self.examples]


@dataclass(frozen=True)
class ThisWeek:
    week: Week
    rows: list[Row] | None

    @property
    def gathering(self) -> bool:
        return self.rows is None


def this_week_on_hn(record: WeeklyWords) -> ThisWeek | None:
    latest = record.latest()
    if latest is None:
        return None
    words = record.weeks[latest]
    found = risers(words, record.before(latest, BASELINE_WEEKS))
    rows = None if found is None else [Row(riser, words.risers.get(riser.term, [])) for riser in found]
    return ThisWeek(latest, rows)


def _escaped(markdown: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+!|$<>~-])", r"\\\1", markdown)


def _times(rise: float) -> str:
    return f"{rise:.0f}×" if rise >= 10 else f"{rise:.1f}×"
