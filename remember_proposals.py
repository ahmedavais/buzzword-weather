import sys
from pathlib import Path

from buzzword_weather.weekly_words import WeeklyWords

WEEKLY_WORDS = Path(__file__).parent / "weekly_words.json"


def main(slugs: list[str]) -> None:
    record = WeeklyWords.from_json(WEEKLY_WORDS.read_text())
    WEEKLY_WORDS.write_text(record.with_proposed(set(slugs)).to_json())


if __name__ == "__main__":
    main(sys.argv[1:])
