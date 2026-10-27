from buzzword_weather.titles import terms_in


def test_finds_words_and_two_word_phrases_in_lowercase():
    assert terms_in("Rust compiler internals") == {
        "rust",
        "compiler",
        "internals",
        "rust compiler",
        "compiler internals",
    }


def test_counts_a_repeated_word_once():
    assert terms_in("Rust, Rust everywhere") == {"rust", "everywhere", "rust everywhere"}


def test_never_pairs_words_across_punctuation():
    assert "databases rust" not in terms_in("Databases: Rust edition")


def test_leaves_out_common_english_words_and_never_bridges_them():
    assert terms_in("The state of the art") == {"state", "art"}


def test_leaves_out_hacker_news_prefixes():
    assert terms_in("Show HN: Tiny databases") == {"tiny", "databases", "tiny databases"}
    assert terms_in("Ask HN – Who is hiring?") == {"hiring"}
    assert terms_in("Launch HN: Acme (YC W26) – Invoices") >= {"acme", "invoices"}


def test_leaves_out_bracketed_tags_and_parenthesized_years():
    assert terms_in("Garbage collection handbook [pdf] (2019)") == {
        "garbage",
        "collection",
        "handbook",
        "garbage collection",
        "collection handbook",
    }


def test_leaves_out_bare_numbers_and_years():
    assert terms_in("Postgres 18 released in 2026") == {"postgres", "released"}


def test_keeps_language_and_model_names_whole():
    assert terms_in("C++ vs. C# vs. Node.js vs. GPT-5") >= {"c++", "c#", "node.js", "gpt-5"}


def test_keeps_hyphenated_words_whole():
    assert "low-code" in terms_in("Low-code tools are back")


def test_drops_possessives():
    assert terms_in("Apple’s new chip") == {"apple", "chip"}


def test_leaves_out_the_words_of_the_site_the_story_links_to():
    assert terms_in("GitHub Copilot pricing", url="https://github.blog/news/copilot") == {
        "copilot",
        "pricing",
        "copilot pricing",
    }


def test_keeps_every_word_when_the_story_links_nowhere():
    assert "github" in terms_in("GitHub Copilot pricing", url=None)


def test_leaves_out_money_amounts():
    assert terms_in("$25B gas venture, $10k bounty, 3x faster") == {"gas", "venture", "gas venture", "bounty", "faster"}


def test_leaves_out_cve_ids():
    assert terms_in("PHP2Shell (CVE-2026-109618) exploit") == {"php2shell", "exploit"}
