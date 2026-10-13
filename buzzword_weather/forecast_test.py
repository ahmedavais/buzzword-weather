from buzzword_weather.forecast import Weather, weather_of


def test_calls_a_term_calm_when_no_month_reached_ten_mentions():
    assert weather_of([0, 2, 9, 4, 3, 1]) == Weather.CALM


def test_calls_a_storm_passing_when_the_last_two_months_average_half_the_peak_or_less():
    assert weather_of([0, 1, 32, 43, 19, 6]) == Weather.STORM_PASSING


def test_calls_a_front_moving_in_when_the_last_two_months_run_well_above_three_to_six_months_back():
    assert weather_of([10, 10, 10, 12, 15, 16]) == Weather.FRONT_MOVING_IN


def test_calls_a_steady_breeze_when_nothing_changed_much():
    assert weather_of([30, 34, 27, 31, 36, 30]) == Weather.STEADY_BREEZE


def test_calls_a_brand_new_term_a_front_moving_in():
    assert weather_of([0, 0, 0, 0, 20, 25]) == Weather.FRONT_MOVING_IN


def test_reads_like_a_forecast():
    assert Weather.STORM_PASSING.forecast == "a storm passing"
