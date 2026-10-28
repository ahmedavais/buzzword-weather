import re

from buzzword_weather.weekly_words import Example

MARKDOWN = re.compile(r"([\\`*_{}\[\]()#+!|$<>~-])")
WORD_JOINER = "⁠"


def story_link(example: Example) -> str:
    story_id, title = example
    return f"[{inert(title)}](https://news.ycombinator.com/item?id={story_id})"


def inert(text: str) -> str:
    escaped = MARKDOWN.sub(r"\\\1", text)
    return re.sub(r"(@|\\#)", rf"\1{WORD_JOINER}", escaped)
