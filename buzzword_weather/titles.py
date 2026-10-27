import re
from urllib.parse import urlparse

HN_PREFIX = re.compile(r"^\s*(show|ask|launch|tell)\s+hn\b\s*[:–—-]?", re.IGNORECASE)
TAGS = re.compile(r"\[[^\]]*\]|\(\s*(\d{4}|yc [a-z]\d{2})\s*\)", re.IGNORECASE)
TOKEN = re.compile(r"[a-z0-9][a-z0-9+#.'’-]*")
NUMBER = re.compile(r"^(v?[\d.,]+(k|m|b|bn|x|%)?|cve-\d{4}-\d+)$")
TRAILING = ".'’-"

STOPWORDS = frozenset(
    [
        "a", "about", "above", "after", "again", "against", "all", "almost", "also", "am", "among", "an", "and", "any",
        "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
        "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
        "down", "during", "each", "either", "else", "ever", "every", "few", "for", "from", "further", "get", "gets",
        "getting", "got", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "her", "here", "hers",
        "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "it's", "its",
        "itself", "just", "let", "like", "made", "make", "makes", "making", "many", "may", "me", "might", "more",
        "most", "much", "must", "my", "myself", "new", "no", "nor", "not", "now", "of", "off", "on", "once", "one",
        "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "per", "really", "same", "say", "says",
        "see", "she", "should", "shouldn't", "so", "some", "still", "such", "than", "that", "that's", "the", "their",
        "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "this", "those", "through", "to",
        "too", "under", "until", "up", "upon", "us", "use", "used", "uses", "using", "via", "vs", "vs.", "want", "was",
        "wasn't", "way", "ways", "we", "were", "weren't", "what", "what's", "when", "where", "which", "while", "who",
        "whom", "whose", "why", "will", "with", "without", "won't", "would", "wouldn't", "yet", "you", "your", "yours",
        "yourself", "yourselves", "hn"
    ]
)


def terms_in(title: str, url: str | None = None) -> set[str]:
    words = _words(title, _site_words(url))
    pairs = {f"{first} {second}" for first, second in zip(words, words[1:], strict=False) if first and second}
    return {word for word in words if word} | pairs


def _words(title: str, site_words: set[str]) -> list[str | None]:
    text = TAGS.sub(" | ", HN_PREFIX.sub("", title)).lower()
    pieces = re.split(r"(\s+|[^a-z0-9+#.'’\s-]+)", text)
    return [_kept(piece, site_words) for piece in pieces if piece and not piece.isspace()]


def _kept(piece: str, site_words: set[str]) -> str | None:
    match = TOKEN.fullmatch(piece)
    if not match:
        return None
    word = re.sub(r"['’]s$", "", piece.rstrip(TRAILING)).rstrip(TRAILING)
    if len(word) < 2 or word in STOPWORDS or word in site_words or NUMBER.match(word):
        return None
    return word


def _site_words(url: str | None) -> set[str]:
    host = urlparse(url).hostname if url else None
    return set(host.removeprefix("www.").split(".")) if host else set()
