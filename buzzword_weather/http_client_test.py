import pytest

from buzzword_weather.http_client import Answer, HttpClient


def test_answers_a_nulled_request_with_the_configured_body():
    http = HttpClient.create_null(bodies='{"nbHits": 3}')

    assert http.get_json("https://example.test/search", {"query": "x"}) == {"nbHits": 3}


def test_answers_with_configured_bodies_in_order_then_fails_fast():
    http = HttpClient.create_null(bodies=['{"a": 1}', '{"a": 2}'])

    assert http.get_json("https://example.test", {})["a"] == 1
    assert http.get_json("https://example.test", {})["a"] == 2
    with pytest.raises(AssertionError, match="No more responses configured"):
        http.get_json("https://example.test", {})


def test_answers_each_url_from_its_own_configured_bodies():
    http = HttpClient.create_null(bodies={"https://example.test/search": ['{"a": 1}', '{"a": 2}'], "https://example.test/latest": '{"b": 9}'})

    assert http.get_json("https://example.test/search", {"query": "x"})["a"] == 1
    assert http.get_json("https://example.test/latest", {})["b"] == 9
    assert http.get_json("https://example.test/search", {"query": "y"})["a"] == 2


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


def test_waits_and_tries_again_when_the_server_says_slow_down():
    http = HttpClient.create_null(bodies=[Answer(429, "Too Many Requests"), '{"nbHits": 4}'])
    pauses = http.track_pauses()

    assert http.get_json("https://example.test", {}) == {"nbHits": 4}
    assert pauses.data == [1.0]


def test_waits_longer_each_time_it_is_refused():
    http = HttpClient.create_null(bodies=[Answer(403, "Forbidden"), Answer(403, "Forbidden"), '{"nbHits": 4}'])
    pauses = http.track_pauses()

    http.get_json("https://example.test", {})

    assert pauses.data == [1.0, 2.0]


def test_gives_up_with_a_detailed_error_after_its_last_try():
    http = HttpClient.create_null(bodies=Answer(429, "Too Many Requests"))

    with pytest.raises(ValueError, match="https://example.test.*gave up after 4 tries.*429"):
        http.get_json("https://example.test", {})


def test_fails_at_once_on_a_server_error():
    http = HttpClient.create_null(bodies=Answer(500, "Internal Server Error"))
    pauses = http.track_pauses()

    with pytest.raises(ValueError, match="https://example.test.*answered 500.*Internal Server Error"):
        http.get_json("https://example.test", {})
    assert pauses.data == []


def test_tries_again_when_a_request_times_out():
    http = HttpClient.create_null(bodies=[Answer.timed_out(), '{"nbHits": 4}'])
    pauses = http.track_pauses()

    assert http.get_json("https://example.test", {}) == {"nbHits": 4}
    assert pauses.data == [1.0]
