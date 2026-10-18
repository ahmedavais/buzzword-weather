from html import escape

from buzzword_weather.forecast import Weather


def weather_legend(weathers: dict[str, Weather], colors: dict[str, str]) -> str:
    rows = [
        f'<div><span style="color: {colors[buzzword]}">●</span> {weather.icon} {escape(buzzword)}: {weather.forecast}</div>'
        for buzzword, weather in weathers.items()
    ]
    return "".join(rows)
