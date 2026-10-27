from datetime import date

from buzzword_weather.hacker_news import HackerNews, Story
from buzzword_weather.periods import Week
from buzzword_weather.rising import BASELINE_WEEKS
from buzzword_weather.week_recorder import record_missing_weeks, words_of_week
from buzzword_weather.weekly_words import WEEKS_KEPT, WeeklyWords, WeekOfWords

MONDAY = date(2026, 11, 2)
JUST_ENDED = Week(2026, 44)


def stories_titled(*titles: str) -> list[Story]:
    return [Story(number, title) for number, title in enumerate(titles, start=1)]


def test_counts_the_stories_using_each_term_and_every_title():
    week = words_of_week(stories_titled("Rust in prod", "Rust at work", "Rust for fun", "Go for fun"), [])

    assert week.titles == 4
    assert week.stories == {"rust": 3}


def test_keeps_up_to_3_example_titles_for_each_riser():
    titles = [f"MCP for {animal}" for animal in ["cats", "dogs", "owls", "bats", "eels"]]
    quiet = [WeekOfWords(1000, {})] * BASELINE_WEEKS

    week = words_of_week(stories_titled(*titles), quiet)

    assert week.risers["mcp"] == [(3, titles[2]), (4, titles[3]), (5, titles[4])]


def test_keeps_no_examples_while_still_gathering():
    assert words_of_week(stories_titled(*["MCP server"] * 3), []).risers == {}


def test_records_every_finished_week_it_lacks_oldest_first():
    hacker_news = HackerNews.create_null(stories=stories_titled("Rust in prod"))
    recorded: list[Week] = []

    record = record_missing_weeks(WeeklyWords(), hacker_news, MONDAY, recorded.append)

    assert len(recorded) == WEEKS_KEPT
    assert recorded[-1] == JUST_ENDED
    assert record.latest() == JUST_ENDED


def test_asks_hacker_news_for_nothing_when_every_week_is_recorded():
    hacker_news = HackerNews.create_null()
    first = record_missing_weeks(WeeklyWords(), hacker_news, MONDAY, lambda week: None)
    slices = hacker_news.track_story_slices()

    again = record_missing_weeks(first, hacker_news, MONDAY, lambda week: None)

    assert again == first
    assert slices.data == []


def test_asks_for_each_week_from_monday_to_monday():
    hacker_news = HackerNews.create_null()
    slices = hacker_news.track_story_slices()
    almost_full = WeeklyWords({week: WeekOfWords(1, {}) for week in [JUST_ENDED.previous()]})

    record_missing_weeks(almost_full, hacker_news, MONDAY, lambda week: None)

    assert slices.data[-1][1] == JUST_ENDED.ends_at
