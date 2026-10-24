from html import escape

from buzzword_weather.forecast import Weather

SUMMARIES = {
    Weather.CLEAR_SKIES: "No significant activity.",
    Weather.FIRST_CLOUDS: "A new term is gathering attention.",
    Weather.FRONT_MOVING_IN: "Mentions are accelerating.",
    Weather.STORM_OVERHEAD: "Near its recorded peak.",
    Weather.STORM_PASSING: "Interest has dropped from a recent peak.",
    Weather.CLEARING_SKIES: "Far below an older peak.",
    Weather.STEADY_BREEZE: "Holding its usual level.",
}


def forecast_card(name: str, weather: Weather, latest_rate: float) -> str:
    return (
        f"<h3>{weather.icon} {escape(name)}</h3>"
        f"<p>{SUMMARIES[weather]}</p>"
        f"<p>{latest_rate:.2f} mentions per 10,000 posts</p>"
    )
