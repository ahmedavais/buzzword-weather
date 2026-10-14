from collections import Counter

from buzzword_weather.forecast import Weather

MOST_IN_ONE_WEATHER = 2


def pick_defaults(pool: list[tuple[str, Weather]], most: int) -> list[str]:
    chosen: set[str] = set()
    per_weather: Counter[Weather] = Counter()
    for name, weather in pool:
        if len(chosen) < most and per_weather[weather] < MOST_IN_ONE_WEATHER:
            chosen.add(name)
            per_weather[weather] += 1
    for name, _ in pool:
        if len(chosen) < most:
            chosen.add(name)
    return [name for name, _ in pool if name in chosen]
