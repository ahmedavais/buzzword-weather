from datetime import date
from pathlib import Path

from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Week
from buzzword_weather.week_recorder import record_missing_weeks
from buzzword_weather.weekly_words import WeeklyWords

WEEKLY_WORDS = Path(__file__).parent / "weekly_words.json"


def main() -> None:
    record = WeeklyWords.from_json(WEEKLY_WORDS.read_text()) if WEEKLY_WORDS.exists() else WeeklyWords()
    record = record_missing_weeks(record, HackerNews.create(), date.today(), on_recorded=print_recorded)
    WEEKLY_WORDS.write_text(record.to_json())


def print_recorded(week: Week) -> None:
    print(f"recorded {week.label}", flush=True)


if __name__ == "__main__":
    main()
