from buzzword_weather.catalog import CATALOG, DEFAULT_POOL, ERAS, search_phrase_for


def test_searches_safe_as_scaled_agile_so_the_everyday_word_stays_out():
    assert search_phrase_for("SAFe") == "scaled agile"


def test_searches_extreme_programming_by_name_so_windows_xp_stays_out():
    assert search_phrase_for("Extreme programming") == "extreme programming"


def test_finds_a_catalog_buzzword_whatever_its_case():
    assert search_phrase_for("safe") == "scaled agile"


def test_searches_a_typed_buzzword_as_typed_in_lowercase():
    assert search_phrase_for("  Agentic Workflows ") == "agentic workflows"


def test_names_each_buzzword_once():
    names = [buzzword.name.lower() for buzzword in CATALOG]

    assert len(names) == len(set(names))


def test_places_every_buzzword_in_a_known_era():
    assert {buzzword.era for buzzword in CATALOG} <= set(ERAS)


def test_keeps_an_era_for_buzzwords_promoted_from_rising_words():
    assert "rising" in ERAS


def test_draws_defaults_from_a_pool_of_catalog_buzzwords():
    assert set(DEFAULT_POOL) <= {buzzword.name for buzzword in CATALOG}
