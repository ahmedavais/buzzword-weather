from buzzword_weather.rising import BASELINE_WEEKS, Heat, Riser, risers
from buzzword_weather.weekly_words import WeekOfWords

TITLES = 10_000


def quiet_weeks(**stories: int) -> list[WeekOfWords]:
    return [WeekOfWords(TITLES, dict(stories))] * BASELINE_WEEKS


def this_week(**stories: int) -> WeekOfWords:
    return WeekOfWords(TITLES, {term.replace("_", " "): count for term, count in stories.items()})


def terms(found: list[Riser] | None) -> list[str]:
    return [riser.term for riser in found or []]


def test_measures_a_jump_against_the_12_weeks_before():
    [crowdstrike] = risers(this_week(crowdstrike=40), [WeekOfWords(TITLES * 2, {"crowdstrike": 1})] * BASELINE_WEEKS)

    assert crowdstrike.rate == 40
    assert crowdstrike.usual == 0.5
    assert crowdstrike.rise == 80


def test_is_still_gathering_with_fewer_than_12_weeks_before():
    assert risers(this_week(rust=40), quiet_weeks(rust=1)[1:]) is None


def test_compares_with_only_the_latest_12_weeks():
    weeks_before = [WeekOfWords(TITLES, {"rust": 100})] + quiet_weeks(rust=10)

    assert risers(this_week(rust=40), weeks_before)[0].usual == 10


def test_ranks_only_words_at_twice_their_usual_rate_or_more():
    assert terms(risers(this_week(rust=19, go=20), quiet_weeks(rust=10, go=10))) == ["go"]


def test_ranks_a_word_too_rare_to_record_before_first_as_a_new_front():
    found = risers(this_week(rust=90, mcp=5), quiet_weeks(rust=1))

    assert terms(found) == ["mcp", "rust"]
    assert found[0].heat is Heat.NEW_FRONT


def test_orders_new_words_by_their_rate_this_week():
    assert terms(risers(this_week(mcp=5, sora=9), quiet_weeks())) == ["sora", "mcp"]


def test_orders_the_others_by_how_far_they_rose():
    assert terms(risers(this_week(rust=30, go=50), quiet_weeks(rust=5, go=20))) == ["rust", "go"]


def test_never_ranks_a_word_from_fewer_than_3_stories():
    assert terms(risers(this_week(mcp=2), quiet_weeks())) == []


def test_shows_at_most_10_words():
    many = {f"word{number}": 10 for number in range(15)}

    assert len(risers(WeekOfWords(TITLES, many), quiet_weeks())) == 10


def test_shows_a_phrase_instead_of_a_word_mostly_used_inside_it():
    found = risers(this_week(claude_code=30, claude=35, code=200), quiet_weeks(claude=5, code=190))

    assert terms(found) == ["claude code"]


def test_keeps_a_word_that_rises_mostly_outside_the_phrase():
    found = risers(this_week(crowdstrike_outage=10, crowdstrike=40), quiet_weeks(crowdstrike=1))

    assert set(terms(found)) == {"crowdstrike", "crowdstrike outage"}


def test_names_the_heat_by_how_far_a_word_rose():
    assert Riser("a", rate=12, usual=2).heat is Heat.WILDFIRE
    assert Riser("a", rate=6, usual=2).heat is Heat.HEATWAVE
    assert Riser("a", rate=5.9, usual=2).heat is Heat.WARM
    assert Riser("a", rate=4, usual=2).heat is Heat.WARM


def test_counts_a_word_too_rare_to_record_as_just_under_the_floor():
    assert risers(this_week(mcp=3), quiet_weeks()) == []
    [mcp] = risers(this_week(mcp=4), quiet_weeks())

    assert mcp.usual == 2
    assert mcp.rise == 2


def test_is_a_new_front_only_when_under_the_floor_in_every_week_before():
    weeks_before = quiet_weeks()[1:] + [WeekOfWords(TITLES, {"mcp": 3})]

    [mcp] = risers(this_week(mcp=40), weeks_before)

    assert not mcp.is_new
