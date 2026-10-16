from buzzword_weather.forecast import Weather, weather_of

QUIET_HISTORY = [0] * 70 + [0.03, 0.05, 0.02, 0.04, 0.06, 0.03, 0.02, 0.01, 0]
OLD_BOOM = [0] * 20 + [3, 4, 5, 4.5, 4] + [2] * 46 + [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
STEADY_YEARS = [0] * 30 + [1.5] * 5 + [0.9] * 44


def months(*recent: float) -> list[float]:
    return [0] * (24 - len(recent)) + list(recent)


def test_calls_skies_clear_when_a_term_was_never_busy():
    assert weather_of(months(0, 0.06, 0.27, 0.12, 0.09, 0.03), QUIET_HISTORY) == Weather.CLEAR_SKIES


def test_sees_first_clouds_when_a_new_term_is_still_near_its_first_peak():
    assert weather_of(months(0.12, 0.27, 0.42, 0.54, 0.51, 0.57), [0] * 77 + [0.27, 0.54]) == Weather.FIRST_CLOUDS


def test_calls_a_new_term_that_already_faded_a_storm_passing():
    assert weather_of(months(0, 0.03, 0.96, 1.29, 0.57, 0.18), [0] * 77 + [0.01, 0.68]) == Weather.STORM_PASSING


def test_calls_skies_clearing_when_a_term_is_long_past_its_all_time_peak():
    assert weather_of([0.9] * 22 + [0.81, 0.75], OLD_BOOM) == Weather.CLEARING_SKIES


def test_calls_a_storm_passing_when_the_last_two_months_average_half_the_recent_peak_or_less():
    assert weather_of([3] * 18 + [12, 28.5, 21, 15, 12.3, 12.6], STEADY_YEARS[:-3] + [6, 19, 13]) == Weather.STORM_PASSING


def test_calls_a_front_moving_in_when_the_last_two_months_run_well_above_three_to_six_months_back():
    assert weather_of([0.6] * 18 + [0.6, 0.6, 0.66, 0.9, 1.08, 1.2], STEADY_YEARS[:-1] + [1.0]) == Weather.FRONT_MOVING_IN


def test_calls_a_storm_overhead_when_the_last_quarter_is_near_its_all_time_peak():
    assert weather_of([0.6] * 18 + [0.9, 1.02, 0.81, 0.93, 1.08, 0.9], [0] * 75 + [0.6, 0.9, 0.92, 0.97]) == Weather.STORM_OVERHEAD


def test_calls_a_steady_breeze_when_nothing_changed_much():
    assert weather_of([0.9] * 24, STEADY_YEARS) == Weather.STEADY_BREEZE


def test_reads_like_a_forecast():
    assert Weather.CLEARING_SKIES.forecast == "clearing skies"


def test_shows_a_different_icon_for_every_forecast():
    assert len({weather.icon for weather in Weather}) == len(Weather)
