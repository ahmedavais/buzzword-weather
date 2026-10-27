import sys
from pathlib import Path

from buzzword_weather.candidates import candidates, with_candidate
from buzzword_weather.catalog import CATALOG
from buzzword_weather.weekly_words import WeeklyWords

ROOT = Path(__file__).parent
CATALOG_FILE = ROOT / "buzzword_weather" / "catalog.py"


def main(phrase: str) -> None:
    record = WeeklyWords.from_json((ROOT / "weekly_words.json").read_text())
    [candidate] = [found for found in candidates(record, {buzzword.phrase for buzzword in CATALOG}) if found.phrase == phrase]
    CATALOG_FILE.write_text(with_candidate(CATALOG_FILE.read_text(), candidate))


if __name__ == "__main__":
    main(sys.argv[1])
