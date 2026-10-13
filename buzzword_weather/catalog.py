from dataclasses import dataclass

ERAS = ["process", "architecture", "data", "hype", "the AI era"]


@dataclass(frozen=True)
class Buzzword:
    name: str
    era: str
    phrase: str


def _buzzword(name: str, era: str, phrase: str | None = None) -> Buzzword:
    return Buzzword(name, era, phrase or name.lower())


CATALOG = [
    _buzzword("Agile", "process"),
    _buzzword("Scrum", "process"),
    _buzzword("Kanban", "process"),
    _buzzword("Extreme programming", "process"),
    _buzzword("SAFe", "process", "scaled agile"),
    _buzzword("DevOps", "process"),
    _buzzword("Lean startup", "process"),
    _buzzword("SOA", "architecture", "service oriented architecture"),
    _buzzword("Microservices", "architecture"),
    _buzzword("Serverless", "architecture"),
    _buzzword("Cloud native", "architecture"),
    _buzzword("Low-code", "architecture"),
    _buzzword("Big data", "data"),
    _buzzword("NoSQL", "data"),
    _buzzword("Web 2.0", "hype"),
    _buzzword("Blockchain", "hype"),
    _buzzword("Web3", "hype"),
    _buzzword("Metaverse", "hype"),
    _buzzword("Prompt engineering", "the AI era"),
    _buzzword("Context engineering", "the AI era"),
    _buzzword("Vibe coding", "the AI era"),
    _buzzword("Harness engineering", "the AI era"),
    _buzzword("Loop engineering", "the AI era"),
    _buzzword("Ralph loop", "the AI era"),
    _buzzword("Platform engineering", "the AI era"),
]

DEFAULT_NAMES = ["Vibe coding", "Harness engineering", "Loop engineering", "Ralph loop", "Platform engineering"]

_BY_NAME = {buzzword.name.lower(): buzzword for buzzword in CATALOG}


def search_phrase_for(name: str) -> str:
    typed = name.strip().lower()
    known = _BY_NAME.get(typed)
    return known.phrase if known else typed
