import pytest

from buzzword_weather.http_client import HttpClient


def test_answers_a_nulled_request_with_the_configured_body():
    http = HttpClient.create_null(bodies='{"nbHits": 3}')

    assert http.get_json("https://example.test/search", {"query": "x"}) == {"nbHits": 3}


def test_answers_with_configured_bodies_in_order_then_fails_fast():
    http = HttpClient.create_null(bodies=['{"a": 1}', '{"a": 2}'])

    assert http.get_json("https://example.test", {})["a"] == 1
    assert http.get_json("https://example.test", {})["a"] == 2
    with pytest.raises(AssertionError, match="No more responses configured"):
        http.get_json("https://example.test", {})


def test_answers_a_bare_nulled_request_with_a_self_naming_body():
    assert HttpClient.create_null().get_json("https://example.test", {}) == {"nulled": "Nulled HttpClient default body"}


def test_tracks_each_request_it_sends():
    http = HttpClient.create_null()
    requests = http.track_requests()

    http.get_json("https://example.test/search", {"query": '"vibe coding"', "hitsPerPage": 0})

    assert requests.data == [{"url": "https://example.test/search", "params": {"query": '"vibe coding"', "hitsPerPage": 0}}]


def test_fails_with_a_detailed_error_when_the_body_is_not_json():
    http = HttpClient.create_null(bodies="<html>rate limited</html>")

    with pytest.raises(ValueError, match="https://example.test.*not JSON.*rate limited"):
        http.get_json("https://example.test", {})


@pytest.mark.integration
def test_reads_a_real_hacker_news_search_as_json():
    answer = HttpClient.create().get_json("https://hn.algolia.com/api/v1/search", {"query": '"vibe coding"', "hitsPerPage": 0})

    assert isinstance(answer["nbHits"], int)
