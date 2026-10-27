from buzzword_weather.periods import Week
from buzzword_weather.rising import BASELINE_WEEKS, Riser
from buzzword_weather.this_week import Row, this_week_on_hn
from buzzword_weather.weekly_words import WeeklyWords, WeekOfWords

LATEST = Week(2026, 44)


def record_ending_with(latest: WeekOfWords, weeks_before: int = BASELINE_WEEKS) -> WeeklyWords:
    record = WeeklyWords()
    week = LATEST
    for _ in range(weeks_before):
        week = week.previous()
        record = record.with_week(week, WeekOfWords(10_000, {"rust": 5}))
    return record.with_week(LATEST, latest)


def test_shows_nothing_without_a_recorded_week():
    assert this_week_on_hn(WeeklyWords()) is None


def test_is_still_gathering_without_12_weeks_before_the_latest():
    this_week = this_week_on_hn(record_ending_with(WeekOfWords(10_000, {"rust": 50}), weeks_before=11))

    assert this_week.week == LATEST
    assert this_week.gathering


def test_shows_the_latest_week_risers_with_their_example_titles():
    latest = WeekOfWords(10_000, {"rust": 50}, {"rust": [(7, "Rust in the kernel")]})

    [row] = this_week_on_hn(record_ending_with(latest)).rows

    assert row.riser.term == "rust"
    assert row.examples == [(7, "Rust in the kernel")]


def test_shows_a_quiet_week_as_no_rows():
    this_week = this_week_on_hn(record_ending_with(WeekOfWords(10_000, {"rust": 5})))

    assert this_week.rows == []
    assert not this_week.gathering


def test_headlines_a_row_with_heat_rise_and_rate():
    assert Row(Riser("rust", rate=80, usual=1), []).headline == "🔥 **rust** · wildfire · 80× usual · 80.0 per 10,000 titles"
    assert Row(Riser("rust", rate=5, usual=2), []).headline == "☀️ **rust** · warm · 2.5× usual · 5.0 per 10,000 titles"


def test_headlines_a_new_word_without_a_rise():
    assert "never seen in the 12 weeks before" in Row(Riser("mcp", rate=3, usual=0), []).headline


def test_links_each_example_title_to_its_hacker_news_discussion():
    row = Row(Riser("rust", rate=8, usual=1), [(7, "Rust in the kernel")])

    assert row.example_links == ["[Rust in the kernel](https://news.ycombinator.com/item?id=7)"]


def test_escapes_markdown_in_titles():
    row = Row(Riser("rust", rate=8, usual=1), [(7, "Rust [pdf] costs $5 *now*")])

    assert row.example_links == [r"[Rust \[pdf\] costs \$5 \*now\*](https://news.ycombinator.com/item?id=7)"]
