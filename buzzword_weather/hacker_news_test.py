from datetime import date

import pytest

from buzzword_weather.hacker_news import BY_DATE_URL, SLICE_SECONDS, HackerNews, Story
from buzzword_weather.http_client import HttpClient
from buzzword_weather.periods import Month, finished_weeks_before

MARCH = Month(2026, 3)


def test_counts_the_mentions_of_a_term_in_a_month():
    assert HackerNews.create_null(mentions=42).mentions("vibe coding", MARCH) == 42


def test_counts_each_period_in_turn():
    hacker_news = HackerNews.create_null(mentions=[3, 5])

    assert hacker_news.mentions_by_period("ralph loop", [Month(2026, 2), MARCH]) == [3, 5]


def test_counts_no_mentions_in_a_bare_nulled_world():
    assert HackerNews.create_null().mentions("anything", MARCH) == 0


def test_searches_stories_and_comments_for_the_exact_phrase_within_the_month():
    http = HttpClient.create_null(bodies='{"nbHits": 1}')
    requests = http.track_requests()

    HackerNews(http).mentions("harness engineering", MARCH)

    assert requests.data == [
        {
            "url": "https://hn.algolia.com/api/v1/search",
            "params": {
                "query": '"harness engineering"',
                "tags": "(story,comment)",
                "numericFilters": f"created_at_i>={MARCH.starts_at},created_at_i<{MARCH.ends_at}",
                "hitsPerPage": 0,
            },
        }
    ]


def test_tracks_each_search_by_term_and_period():
    hacker_news = HackerNews.create_null()
    searches = hacker_news.track_searches()

    hacker_news.mentions("loop engineering", MARCH)

    assert searches.data == [{"term": "loop engineering", "period": MARCH}]


def test_fails_with_a_detailed_error_when_the_answer_has_no_count():
    http = HttpClient.create_null(bodies='{"message": "Too many requests"}')

    with pytest.raises(ValueError, match="no mention count.*vibe coding.*Mar 2026.*Too many requests"):
        HackerNews(http).mentions("vibe coding", MARCH)


def test_counts_the_items_posted_before_a_month_began():
    assert HackerNews.create_null(items_posted=46_000_000).items_posted_before(MARCH) == 46_000_000


def test_asks_for_the_newest_item_of_any_kind_from_before_the_month():
    http = HttpClient.create_null(bodies='{"hits": [{"objectID": "46000000"}]}')
    requests = http.track_requests()

    HackerNews(http).items_posted_before(MARCH)

    assert requests.data == [
        {
            "url": "https://hn.algolia.com/api/v1/search_by_date",
            "params": {"numericFilters": f"created_at_i<{MARCH.starts_at}", "hitsPerPage": 1},
        }
    ]


def test_fails_with_a_detailed_error_when_the_answer_has_no_item():
    http = HttpClient.create_null(bodies='{"message": "Too many requests"}')

    with pytest.raises(ValueError, match="no newest item.*Mar 2026.*Too many requests"):
        HackerNews(http).items_posted_before(MARCH)


def test_tracks_each_lookup_of_items_posted_by_month():
    hacker_news = HackerNews.create_null()
    lookups = hacker_news.track_item_lookups()

    hacker_news.items_posted_before(MARCH)

    assert lookups.data == [MARCH]


def test_finds_the_stories_posted_in_a_window():
    stories = [Story(2, "Rust in the kernel", "https://lwn.net/a"), Story(1, "Ask HN: Hiring?")]

    assert HackerNews.create_null(stories=stories).stories(0, SLICE_SECONDS) == [stories[1], stories[0]]


def test_asks_for_story_titles_and_links_slice_by_slice():
    http = HttpClient.create_null(bodies='{"nbHits": 0, "hits": []}')
    requests = http.track_requests()

    HackerNews(http).stories(0, 2 * SLICE_SECONDS)

    assert [request["params"] for request in requests.data] == [
        {
            "tags": "story",
            "numericFilters": f"created_at_i>={start},created_at_i<{start + SLICE_SECONDS}",
            "hitsPerPage": 1000,
            "attributesToRetrieve": "title,url",
            "attributesToHighlight": "",
        }
        for start in (0, SLICE_SECONDS)
    ]


def test_halves_a_slice_that_holds_more_stories_than_one_answer_returns():
    http = HttpClient.create_null(
        bodies=[
            '{"nbHits": 2, "hits": [{"objectID": "1", "title": "First"}]}',
            '{"nbHits": 1, "hits": [{"objectID": "1", "title": "First"}]}',
            '{"nbHits": 1, "hits": [{"objectID": "2", "title": "Second"}]}',
        ]
    )
    hacker_news = HackerNews(http)
    slices = hacker_news.track_story_slices()

    stories = hacker_news.stories(0, 100)

    assert [story.title for story in stories] == ["First", "Second"]
    assert slices.data == [(0, 100), (0, 50), (50, 100)]


def test_fails_with_a_detailed_error_when_the_answer_has_no_stories():
    http = HttpClient.create_null(bodies='{"message": "Too many requests"}')

    with pytest.raises(ValueError, match="no stories.*Too many requests"):
        HackerNews(http).stories(0, 100)


@pytest.mark.integration
def test_returns_every_story_a_real_slice_reports():
    week_ago = finished_weeks_before(date.today(), count=1)[0]
    starts_at, ends_at = week_ago.starts_at, week_ago.starts_at + SLICE_SECONDS
    reported = HttpClient.create().get_json(BY_DATE_URL, {"tags": "story", "numericFilters": f"created_at_i>={starts_at},created_at_i<{ends_at}", "hitsPerPage": 0})

    stories = HackerNews.create().stories(starts_at, ends_at)

    assert len(stories) == reported["nbHits"] > 0
    assert all(story.title for story in stories)


def test_finds_no_stories_in_a_bare_nulled_world():
    assert HackerNews.create_null().stories(0, SLICE_SECONDS) == []
