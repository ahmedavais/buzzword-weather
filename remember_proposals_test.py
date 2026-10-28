from pathlib import Path

from buzzword_weather.periods import Week
from buzzword_weather.weekly_words import WeeklyWords, WeekOfWords
from remember_proposals import main

WEEK = Week(2026, 44)


def test_adds_the_proposed_slugs_and_keeps_the_weeks(tmp_path: Path):
    weekly_words = tmp_path / "weekly_words.json"
    recorded = WeeklyWords().with_proposed({"rust"}).with_week(WEEK, WeekOfWords(8000, {"mcp": 12}))
    weekly_words.write_text(recorded.to_json())

    main(["mcp", "c-plus-plus"], weekly_words)

    remembered = WeeklyWords.from_json(weekly_words.read_text())
    assert remembered.proposed == {"rust", "mcp", "c-plus-plus"}
    assert remembered.weeks == recorded.weeks
