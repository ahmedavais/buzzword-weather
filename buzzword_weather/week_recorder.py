from collections import defaultdict
from collections.abc import Callable
from datetime import date

from buzzword_weather.hacker_news import HackerNews, Story
from buzzword_weather.periods import Week, finished_weeks_before
from buzzword_weather.rising import BASELINE_WEEKS, risers
from buzzword_weather.titles import terms_in
from buzzword_weather.weekly_words import LEAST_STORIES, WEEKS_KEPT, WeeklyWords, WeekOfWords

MOST_EXAMPLES = 3


def words_of_week(stories: list[Story], weeks_before: list[WeekOfWords]) -> WeekOfWords:
    using: dict[str, list[Story]] = defaultdict(list)
    for story in stories:
        for term in terms_in(story.title, story.url):
            using[term].append(story)
    counted = WeekOfWords(len(stories), {term: len(found) for term, found in using.items() if len(found) >= LEAST_STORIES})
    examples = {riser.term: [(story.id, story.title) for story in using[riser.term][-MOST_EXAMPLES:]] for riser in risers(counted, weeks_before) or []}
    return WeekOfWords(counted.titles, counted.stories, examples)


def record_missing_weeks(record: WeeklyWords, hacker_news: HackerNews, today: date, on_recorded: Callable[[Week], None]) -> WeeklyWords:
    for week in finished_weeks_before(today, WEEKS_KEPT):
        if week not in record.weeks:
            stories = hacker_news.stories(week.starts_at, week.ends_at)
            record = record.with_week(week, words_of_week(stories, record.before(week, BASELINE_WEEKS)))
            on_recorded(week)
    return record
