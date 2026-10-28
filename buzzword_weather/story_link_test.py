from buzzword_weather.story_link import WORD_JOINER, inert, story_link


def test_links_a_title_to_its_hacker_news_discussion():
    assert story_link((7, "Rust in the kernel")) == "[Rust in the kernel](https://news.ycombinator.com/item?id=7)"


def test_escapes_markdown_so_a_title_cannot_break_or_redirect_its_link():
    assert story_link((7, "Rust [pdf] costs $5 *now*")) == r"[Rust \[pdf\] costs \$5 \*now\*](https://news.ycombinator.com/item?id=7)"
    assert story_link((7, "x](https://evil.test) [y")).startswith(r"[x\]\(https://evil.test\) \[y](")


def test_never_mentions_a_person_or_links_an_issue():
    link = story_link((7, "Ask HN: @someuser on #42"))

    assert f"@{WORD_JOINER}someuser" in link
    assert f"\\#{WORD_JOINER}42" in link


def test_makes_any_text_inert_markdown():
    assert inert("*MCP* @team") == f"\\*MCP\\* @{WORD_JOINER}team"
