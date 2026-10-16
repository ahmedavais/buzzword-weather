from datetime import date
from enum import Enum

from buzzword_weather.periods import Period, complete_months_before, complete_quarters_before, complete_quarters_since

HACKER_NEWS_FIRST_YEAR = 2007


class Span(Enum):
    LAST_2_YEARS = "Last 2 years"
    LAST_10_YEARS = "Last 10 years"
    ALL_TIME = "All time"

    @property
    def label(self) -> str:
        return self.value

    @property
    def step(self) -> str:
        return "month" if self is Span.LAST_2_YEARS else "quarter"

    def periods_before(self, day: date) -> list[Period]:
        match self:
            case Span.LAST_2_YEARS:
                return complete_months_before(day, 24)
            case Span.LAST_10_YEARS:
                return complete_quarters_before(day, 40)
            case Span.ALL_TIME:
                return complete_quarters_since(HACKER_NEWS_FIRST_YEAR, before=day)
