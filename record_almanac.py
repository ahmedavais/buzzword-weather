import time
from datetime import date
from pathlib import Path

from buzzword_weather.almanac import Almanac
from buzzword_weather.catalog import CATALOG
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.recorder import record_missing
from buzzword_weather.spans import Span

ALMANAC = Path(__file__).parent / "almanac.json"
PAUSE_SECONDS = 0.25


def main() -> None:
    almanac = Almanac.from_json(ALMANAC.read_text()) if ALMANAC.exists() else Almanac()
    today = date.today()
    periods = Span.LAST_2_YEARS.periods_before(today) + Span.SINCE_2007.periods_before(today)
    hacker_news = HackerNews.create()
    for buzzword in CATALOG:
        almanac = record_missing(almanac, hacker_news, [buzzword.phrase], periods, pause=lambda: time.sleep(PAUSE_SECONDS))
        ALMANAC.write_text(almanac.to_json())
        print(f"recorded {buzzword.name}", flush=True)


if __name__ == "__main__":
    main()
