from pathlib import Path

from buzzword_weather.candidates import Candidate, candidates, watch_list, with_candidate
from buzzword_weather.periods import Week
from buzzword_weather.weekly_words import WeeklyWords, WeekOfWords

CATALOG_SOURCE = (Path(__file__).parent / "catalog.py").read_text()
WEEKS = [Week(2026, number) for number in range(40, 45)]


def record_of(*risers_by_week: list[str]) -> WeeklyWords:
    weeks = {
        week: WeekOfWords(1000, {}, {phrase: [(week.week, f"{phrase.upper()} week {week.week}")] for phrase in risers})
        for week, risers in zip(WEEKS, risers_by_week, strict=False)
    }
    return WeeklyWords(weeks)


def phrases(found: list[Candidate]) -> list[str]:
    return [candidate.phrase for candidate in found]


def test_proposes_a_word_that_rose_in_3_of_the_last_4_weeks():
    found = candidates(record_of(["rust"], ["mcp"], ["mcp"], [], ["mcp"]), catalog_phrases=set())

    assert phrases(found) == ["mcp"]
    assert found[0].weeks == [WEEKS[1], WEEKS[2], WEEKS[4]]


def test_passes_over_one_big_week():
    assert candidates(record_of([], [], [], ["crowdstrike"], []), catalog_phrases=set()) == []


def test_looks_only_at_the_last_4_weeks():
    assert candidates(record_of(["rust"], ["rust"], ["rust"], [], []), catalog_phrases=set()) == []


def test_passes_over_a_phrase_the_catalog_already_has():
    assert candidates(record_of(*[["vibe coding"]] * 4), catalog_phrases={"vibe coding"}) == []


def test_names_a_candidate_as_titles_usually_spell_it():
    [mcp] = candidates(record_of(["mcp"], ["mcp"], ["mcp"]), catalog_phrases=set())

    assert mcp.name == "MCP"


def test_keeps_the_examples_from_the_weeks_it_rose():
    [mcp] = candidates(record_of(["mcp"], ["mcp"], ["mcp"]), catalog_phrases=set())

    assert [story_id for story_id, _ in mcp.examples] == [40, 41, 42]


def test_slugs_a_phrase_for_a_branch_name():
    assert Candidate("claude code", "Claude Code", [], []).slug == "claude-code"


def test_gives_phrases_that_differ_only_in_symbols_their_own_slugs():
    slugs = [Candidate(phrase, phrase, [], []).slug for phrase in ["c++", "c#", "c", "node.js", "node js"]]

    assert slugs == ["c-plus-plus", "c-sharp", "c", "node-dot-js", "node-js"]


def test_adds_a_candidate_to_the_catalog_in_the_rising_era():
    namespace: dict = {}
    candidate = Candidate("claude code", "Claude Code", [], [])

    exec(with_candidate(CATALOG_SOURCE, candidate), namespace)

    assert namespace["CATALOG"][-1] == namespace["Buzzword"]("Claude Code", "rising", "claude code")


def test_searches_a_candidate_by_its_phrase_when_its_name_differs():
    namespace: dict = {}

    exec(with_candidate(CATALOG_SOURCE, Candidate("rust lang", "Rust-lang", [], [])), namespace)

    assert namespace["CATALOG"][-1].phrase == "rust lang"


def test_tells_the_reviewer_why_a_candidate_is_proposed():
    [mcp] = candidates(record_of(["mcp"], ["mcp"], ["mcp"]), catalog_phrases=set())

    assert "in 3 of the last 4 weeks" in mcp.pull_request_body
    assert "- [MCP week 40](https://news.ycombinator.com/item?id=40)" in mcp.pull_request_body


def test_never_mentions_anyone_named_in_a_title():
    record = WeeklyWords({week: WeekOfWords(1000, {}, {"mcp": [(1, "MCP, asks @someuser")]}) for week in WEEKS[:3]})

    [mcp] = candidates(record, catalog_phrases=set())

    assert "@someuser" not in mcp.pull_request_body


def test_watches_a_word_one_rising_week_from_being_proposed():
    record = record_of(["rust"], [], ["mcp"], ["mcp"])

    assert watch_list(record, catalog_phrases=set()) == ["MCP"]


def test_watches_no_word_that_next_week_cannot_lift_to_3_of_4():
    assert watch_list(record_of(["mcp"], ["mcp"], [], []), catalog_phrases=set()) == []


def test_watches_no_word_due_for_a_proposal_or_in_the_catalog():
    record = record_of(["mcp"], ["mcp"], ["mcp", "vibe coding"], ["vibe coding"])

    assert watch_list(record, catalog_phrases={"vibe coding"}) == []


def test_counts_only_the_risers_the_page_shows():
    unseen = [f"word{number}" for number in range(7)] + ["mcp"]

    assert "mcp" not in phrases(candidates(record_of(unseen, unseen, unseen), catalog_phrases=set()))


def test_never_proposes_or_watches_a_word_proposed():
    record = record_of(["mcp"], ["mcp", "sora"], ["mcp", "sora"]).with_proposed({"mcp", "sora"})

    assert candidates(record, catalog_phrases=set()) == []
    assert watch_list(record, catalog_phrases=set()) == []


def test_watches_no_word_whose_nomination_is_still_open_after_its_streak_slips():
    record = record_of(["mcp"], ["mcp"], ["mcp"], []).with_proposed({"mcp"})

    assert watch_list(record, catalog_phrases=set()) == []


def test_watches_only_the_risers_the_page_shows():
    shown = [f"word{number}" for number in range(7)]

    assert "MCP" not in watch_list(record_of([], shown + ["mcp"], shown + ["mcp"]), catalog_phrases=set())
