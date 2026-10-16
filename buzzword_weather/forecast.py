from enum import Enum
from statistics import mean

QUIET_MONTH = 10
QUIET_QUARTER = 30
NEW_TERM_EARLIER_MENTIONS = 5
PASSING_AT_SHARE_OF_RECENT_PEAK = 0.5
CLEARING_AT_SHARE_OF_ALL_TIME_PEAK = 0.4
CLEARING_AFTER_QUARTERS = 8
RISING_AT_MULTIPLE = 1.5
OVERHEAD_AT_SHARE_OF_ALL_TIME_PEAK = 0.8

ICONS = {
    "clear skies": "☀️",
    "first clouds": "🌥️",
    "a front moving in": "🌬️",
    "a storm overhead": "⛈️",
    "a storm passing": "🌦️",
    "clearing skies": "🌤️",
    "a steady breeze": "🍃",
}


class Weather(Enum):
    CLEAR_SKIES = "clear skies"
    FIRST_CLOUDS = "first clouds"
    FRONT_MOVING_IN = "a front moving in"
    STORM_OVERHEAD = "a storm overhead"
    STORM_PASSING = "a storm passing"
    CLEARING_SKIES = "clearing skies"
    STEADY_BREEZE = "a steady breeze"

    @property
    def forecast(self) -> str:
        return self.value

    @property
    def icon(self) -> str:
        return ICONS[self.value]


def weather_of(last_24_months: list[int], all_quarters: list[int]) -> Weather:
    latest = mean(last_24_months[-2:])
    recent_peak = max(last_24_months)
    all_time_peak = max(all_quarters)
    last_quarter = sum(last_24_months[-3:])
    quarters_since_peak = len(all_quarters) - 1 - all_quarters.index(all_time_peak)
    is_new = sum(last_24_months[:-6]) < NEW_TERM_EARLIER_MENTIONS
    if recent_peak < QUIET_MONTH and all_time_peak < QUIET_QUARTER:
        return Weather.CLEAR_SKIES
    if is_new and latest >= PASSING_AT_SHARE_OF_RECENT_PEAK * recent_peak:
        return Weather.FIRST_CLOUDS
    if last_quarter <= CLEARING_AT_SHARE_OF_ALL_TIME_PEAK * all_time_peak and quarters_since_peak >= CLEARING_AFTER_QUARTERS:
        return Weather.CLEARING_SKIES
    if latest <= PASSING_AT_SHARE_OF_RECENT_PEAK * recent_peak:
        return Weather.STORM_PASSING
    if latest >= RISING_AT_MULTIPLE * mean(last_24_months[-6:-3]):
        return Weather.FRONT_MOVING_IN
    if last_quarter >= OVERHEAD_AT_SHARE_OF_ALL_TIME_PEAK * all_time_peak:
        return Weather.STORM_OVERHEAD
    return Weather.STEADY_BREEZE
