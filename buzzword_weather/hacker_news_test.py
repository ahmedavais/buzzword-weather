import pytest

from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.http_client import HttpClient
from buzzword_weather.periods import Month

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
