from buzzword_weather.forecast import Weather, weather_of

QUIET_HISTORY = [0] * 70 + [3, 5, 2, 4, 6, 3, 2, 1, 0]
OLD_BOOM = [0] * 20 + [300, 400, 500, 450, 400] + [200] * 46 + [120, 110, 100, 90, 80, 70, 60, 50]
STEADY_YEARS = [0] * 30 + [150] * 5 + [90] * 44


def months(*recent: int) -> list[int]:
    return [0] * (24 - len(recent)) + list(recent)


def test_calls_skies_clear_when_a_term_was_never_busy():
    assert weather_of(months(0, 2, 9, 4, 3, 1), QUIET_HISTORY) == Weather.CLEAR_SKIES


def test_sees_first_clouds_when_a_new_term_is_still_near_its_first_peak():
    assert weather_of(months(4, 9, 14, 18, 17, 19), [0] * 77 + [27, 54]) == Weather.FIRST_CLOUDS


def test_calls_a_new_term_that_already_faded_a_storm_passing():
    assert weather_of(months(0, 1, 32, 43, 19, 6), [0] * 77 + [1, 68]) == Weather.STORM_PASSING


def test_calls_skies_clearing_when_a_term_is_long_past_its_all_time_peak():
    assert weather_of([30] * 22 + [27, 25], OLD_BOOM) == Weather.CLEARING_SKIES


def test_calls_a_storm_passing_when_the_last_two_months_average_half_the_recent_peak_or_less():
    assert weather_of(months(*([100] * 18), 400, 950, 700, 500, 410, 420), STEADY_YEARS[:-3] + [600, 1900, 1300]) == Weather.STORM_PASSING


def test_calls_a_front_moving_in_when_the_last_two_months_run_well_above_three_to_six_months_back():
    assert weather_of([20] * 18 + [20, 20, 22, 30, 36, 40], STEADY_YEARS[:-1] + [100]) == Weather.FRONT_MOVING_IN


def test_calls_a_storm_overhead_when_the_last_quarter_is_near_its_all_time_peak():
    assert weather_of([20] * 18 + [30, 34, 27, 31, 36, 30], [0] * 75 + [60, 90, 92, 97]) == Weather.STORM_OVERHEAD


def test_calls_a_steady_breeze_when_nothing_changed_much():
    assert weather_of([30] * 24, STEADY_YEARS) == Weather.STEADY_BREEZE


def test_reads_like_a_forecast():
    assert Weather.CLEARING_SKIES.forecast == "clearing skies"


def test_shows_a_different_icon_for_every_forecast():
    assert len({weather.icon for weather in Weather}) == len(Weather)
