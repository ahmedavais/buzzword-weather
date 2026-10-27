import json
from pathlib import Path

from buzzword_weather.candidates import candidates
from buzzword_weather.catalog import CATALOG
from buzzword_weather.weekly_words import WeeklyWords

WEEKLY_WORDS = Path(__file__).parent / "weekly_words.json"


def main() -> None:
    record = WeeklyWords.from_json(WEEKLY_WORDS.read_text())
    for candidate in candidates(record, {buzzword.phrase for buzzword in CATALOG}):
        print(json.dumps({"phrase": candidate.phrase, "name": candidate.name, "slug": candidate.slug, "body": candidate.pull_request_body}))


if __name__ == "__main__":
    main()
