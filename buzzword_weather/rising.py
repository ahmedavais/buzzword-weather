from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from buzzword_weather.weekly_words import LEAST_STORIES, WeekOfWords

BASELINE_WEEKS = 12
MOST_RISERS = 10
LEAST_RISE = 2.0
SAME_STORIES_SHARE = 0.7


class Heat(Enum):
    NEW_FRONT = "new front"
    WILDFIRE = "wildfire"
    HEATWAVE = "heatwave"
    WARM = "warm"

    @property
    def emoji(self) -> str:
        return {"new front": "🌀", "wildfire": "🔥", "heatwave": "🥵", "warm": "☀️"}[self.value]


@dataclass(frozen=True)
class Riser:
    term: str
    rate: float
    usual: float
    is_new: bool = False

    @property
    def rise(self) -> float:
        return self.rate / self.usual if self.usual else float("inf")

    @property
    def heat(self) -> Heat:
        if self.is_new:
            return Heat.NEW_FRONT
        if self.rise >= 6:
            return Heat.WILDFIRE
        return Heat.HEATWAVE if self.rise >= 3 else Heat.WARM


def risers(this_week: WeekOfWords, weeks_before: list[WeekOfWords], stories_using: Mapping[str, set[int]]) -> list[Riser] | None:
    if len(weeks_before) < BASELINE_WEEKS:
        return None
    rising = [riser for riser in (measured(term, this_week, weeks_before) for term in _counted(this_week)) if riser.rise >= LEAST_RISE]
    ranked = sorted(rising, key=lambda riser: (-riser.rise, -riser.rate, riser.term))
    return _top_of_different_stories(ranked, stories_using)


def measured(term: str, this_week: WeekOfWords, weeks_before: list[WeekOfWords]) -> Riser:
    baseline = weeks_before[-BASELINE_WEEKS:]
    usual = sum(week.highest_possible_rate(term) for week in baseline) / len(baseline)
    return Riser(term, this_week.rate(term), usual, is_new=all(term not in week.stories for week in baseline))


def _counted(week: WeekOfWords) -> list[str]:
    return [term for term, stories in week.stories.items() if stories >= LEAST_STORIES]


def _top_of_different_stories(ranked: list[Riser], stories_using: Mapping[str, set[int]]) -> list[Riser]:
    shown: list[Riser] = []
    for riser in ranked:
        if len(shown) == MOST_RISERS:
            break
        if not any(_mostly_same_stories(stories_using[riser.term], stories_using[other.term]) for other in shown):
            shown.append(riser)
    return shown


def _mostly_same_stories(stories: set[int], shown_stories: set[int]) -> bool:
    return len(stories & shown_stories) >= SAME_STORIES_SHARE * len(stories)
