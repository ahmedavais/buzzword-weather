from enum import Enum
from statistics import mean

QUIET_BELOW = 10
PASSING_AT_SHARE_OF_PEAK = 0.5
RISING_AT_MULTIPLE = 1.5


ICONS = {
    "calm": "☀️",
    "a storm passing": "🌦️",
    "a front moving in": "⛈️",
    "a steady breeze": "🍃",
}


class Weather(Enum):
    CALM = "calm"
    STORM_PASSING = "a storm passing"
    FRONT_MOVING_IN = "a front moving in"
    STEADY_BREEZE = "a steady breeze"

    @property
    def forecast(self) -> str:
        return self.value

    @property
    def icon(self) -> str:
        return ICONS[self.value]


def weather_of(monthly_mentions: list[int]) -> Weather:
    peak = max(monthly_mentions)
    latest = mean(monthly_mentions[-2:])
    three_to_six_months_back = mean(monthly_mentions[-6:-3])
    if peak < QUIET_BELOW:
        return Weather.CALM
    if latest <= PASSING_AT_SHARE_OF_PEAK * peak:
        return Weather.STORM_PASSING
    if latest >= RISING_AT_MULTIPLE * three_to_six_months_back:
        return Weather.FRONT_MOVING_IN
    return Weather.STEADY_BREEZE
