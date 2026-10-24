from buzzword_weather.forecast import Weather
from buzzword_weather.forecast_card import forecast_card


def test_shows_a_buzzwords_weather_latest_rate_and_dry_summary():
    card = forecast_card("Vibe coding", Weather.STORM_OVERHEAD, 6.4321)

    assert "⛈️ Vibe coding" in card
    assert "Near its recorded peak." in card
    assert "6.43 mentions per 10,000 posts" in card


def test_escapes_a_typed_buzzword():
    card = forecast_card('<img src=x onerror="alert(1)">', Weather.CLEAR_SKIES, 0)

    assert "<img" not in card
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in card
