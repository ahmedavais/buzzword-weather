from buzzword_weather import rising
from buzzword_weather.rising import BASELINE_WEEKS, Heat, Riser
from buzzword_weather.weekly_words import WeekOfWords

TITLES = 10_000


def quiet_weeks(**stories: int) -> list[WeekOfWords]:
    return [this_week(**stories)] * BASELINE_WEEKS


def this_week(**stories: int) -> WeekOfWords:
    return WeekOfWords(TITLES, {term.replace("_", " "): count for term, count in stories.items()})


def separate_stories(week: WeekOfWords) -> dict[str, set[int]]:
    return {term: {hash((term, number)) for number in range(count)} for term, count in week.stories.items()}


def risers(week: WeekOfWords, weeks_before: list[WeekOfWords], stories_using: dict[str, set[int]] | None = None) -> list[Riser] | None:
    return rising.risers(week, weeks_before, stories_using or separate_stories(week))


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


def test_calls_a_word_too_rare_to_record_before_a_new_front():
    [mcp] = risers(this_week(mcp=5), quiet_weeks())

    assert mcp.heat is Heat.NEW_FRONT
    assert mcp.rise == 2.5


def test_ranks_new_fronts_and_known_words_together_by_rise():
    assert terms(risers(this_week(rust=90, mcp=5), quiet_weeks(rust=3))) == ["rust", "mcp"]


def test_orders_new_fronts_by_their_rate_this_week():
    assert terms(risers(this_week(mcp=5, sora=9), quiet_weeks())) == ["sora", "mcp"]


def test_orders_the_others_by_how_far_they_rose():
    assert terms(risers(this_week(rust=30, go=50), quiet_weeks(rust=5, go=20))) == ["rust", "go"]


def test_never_ranks_a_word_from_fewer_than_3_stories():
    assert terms(risers(this_week(mcp=2), quiet_weeks())) == []


def test_shows_at_most_10_words():
    many = {f"word{number}": 10 for number in range(15)}

    assert len(risers(WeekOfWords(TITLES, many), quiet_weeks())) == 10


def test_leaves_out_a_word_whose_stories_are_mostly_those_of_a_word_shown_above_it():
    week = this_week(emudhra=50, emudhra_intermediate=13, certificates=20, brotli=12)
    stories = {
        "emudhra": set(range(50)),
        "emudhra intermediate": set(range(13)),
        "certificates": set(range(36, 56)),
        "brotli": set(range(100, 112)),
    }

    assert terms(risers(week, quiet_weeks(certificates=2), stories)) == ["emudhra", "brotli"]


def test_keeps_a_word_that_shares_few_of_its_stories_with_those_above_it():
    week = this_week(php2shell=50, php=120)
    stories = {"php2shell": set(range(50)), "php": set(range(30, 150))}

    assert terms(risers(week, quiet_weeks(php=7), stories)) == ["php2shell", "php"]


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


def test_fills_the_top_10_with_words_from_different_stories():
    many = {f"word{number}": 10 for number in range(10)}
    week = WeekOfWords(TITLES, {**many, "agent": 80, "agent skills": 60})
    stories = {**separate_stories(week), "agent skills": set(range(60)), "agent": set(range(80))}

    found = terms(risers(week, quiet_weeks(**dict.fromkeys(many, 2), agent=10, agent_skills=28), stories))

    assert len(found) == 10
    assert "agent" in found
    assert "agent skills" not in found
