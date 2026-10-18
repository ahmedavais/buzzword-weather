from buzzword_weather.forecast import Weather
from buzzword_weather.weather_legend import weather_legend


def test_shows_each_buzzword_with_a_dot_in_its_line_color_then_its_weather():
    legend = weather_legend({"Harness engineering": Weather.STORM_OVERHEAD}, {"Harness engineering": "#3987e5"})

    assert '<span style="color: #3987e5">●</span> ⛈️ Harness engineering: a storm overhead' in legend


def test_shows_a_typed_buzzword_as_text_not_markup():
    typed = '<img src=x onerror="alert(1)">'

    legend = weather_legend({typed: Weather.CLEAR_SKIES}, {typed: "#3987e5"})

    assert "<img" not in legend
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;: clear skies" in legend
