import re

from buzzword_weather.weekly_words import Example

MARKDOWN = re.compile(r"([\\`*_{}\[\]()#+!|$<>~-])")
WORD_JOINER = "⁠"


def story_link(example: Example) -> str:
    story_id, title = example
    return f"[{_inert(title)}](https://news.ycombinator.com/item?id={story_id})"


def _inert(title: str) -> str:
    escaped = MARKDOWN.sub(r"\\\1", title)
    return re.sub(r"(@|\\#)", rf"\1{WORD_JOINER}", escaped)
