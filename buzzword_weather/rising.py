from dataclasses import dataclass
from enum import Enum

from buzzword_weather.weekly_words import LEAST_STORIES, WeekOfWords

BASELINE_WEEKS = 12
MOST_RISERS = 10
LEAST_RISE = 2.0
PART_SHARE = 0.7


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


def risers(this_week: WeekOfWords, weeks_before: list[WeekOfWords]) -> list[Riser] | None:
    if len(weeks_before) < BASELINE_WEEKS:
        return None
    baseline = weeks_before[-BASELINE_WEEKS:]
    rising = [riser for riser in (_riser(term, this_week, baseline) for term in _counted(this_week)) if riser.rise >= LEAST_RISE]
    shown = _without_parts_of_phrases(rising, this_week)
    return sorted(shown, key=lambda riser: (not riser.is_new, -riser.rise, -riser.rate, riser.term))[:MOST_RISERS]


def _counted(week: WeekOfWords) -> list[str]:
    return [term for term, stories in week.stories.items() if stories >= LEAST_STORIES]


def _riser(term: str, this_week: WeekOfWords, baseline: list[WeekOfWords]) -> Riser:
    usual = sum(week.highest_possible_rate(term) for week in baseline) / len(baseline)
    return Riser(term, this_week.rate(term), usual, is_new=all(term not in week.stories for week in baseline))


def _without_parts_of_phrases(rising: list[Riser], week: WeekOfWords) -> list[Riser]:
    hidden = {
        part
        for riser in rising
        if " " in riser.term
        for part in riser.term.split(" ")
        if week.stories[riser.term] >= PART_SHARE * week.stories.get(part, 0)
    }
    return [riser for riser in rising if riser.term not in hidden]
