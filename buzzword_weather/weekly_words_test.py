from buzzword_weather.periods import Week
from buzzword_weather.weekly_words import WEEKS_KEPT, WeeklyWords, WeekOfWords

W44 = Week(2026, 44)


def test_reads_back_what_it_wrote():
    words = WeekOfWords(titles=8000, stories={"rust": 40, "mcp": 12}, risers={"mcp": [(1, "MCP everywhere")]})
    record = WeeklyWords().with_week(W44, words)

    assert WeeklyWords.from_json(record.to_json()) == record


def test_an_empty_record_has_no_latest_week():
    assert WeeklyWords().latest() is None
    assert WeeklyWords.from_json("{}").latest() is None


def test_rates_a_term_per_10000_titles():
    assert WeekOfWords(titles=8000, stories={"rust": 40}).rate("rust") == 50.0
    assert WeekOfWords(titles=8000, stories={}).rate("rust") == 0.0


def test_keeps_only_the_newest_weeks():
    record = WeeklyWords()
    week = W44
    for _ in range(WEEKS_KEPT + 2):
        record = record.with_week(week, WeekOfWords(titles=1, stories={}))
        week = week.next()

    assert len(record.recorded_weeks()) == WEEKS_KEPT
    assert record.latest() == week.previous()


def test_finds_the_weeks_just_before_a_week_oldest_first():
    record = WeeklyWords()
    for titles, week in enumerate([W44.previous().previous(), W44.previous(), W44]):
        record = record.with_week(week, WeekOfWords(titles=titles, stories={}))

    assert [words.titles for words in record.before(W44, count=1)] == [1]
    assert [words.titles for words in record.before(W44, count=12)] == [0, 1]
