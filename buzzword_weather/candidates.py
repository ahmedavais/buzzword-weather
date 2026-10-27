import json
import re
from collections import Counter
from dataclasses import dataclass

from buzzword_weather.periods import Week
from buzzword_weather.story_link import story_link
from buzzword_weather.weekly_words import Example, WeeklyWords

WEEKS_LOOKED_AT = 4
LEAST_WEEKS_RISEN = 3
CATALOG_START = "CATALOG = ["
CATALOG_END = "\n]\n"


@dataclass(frozen=True)
class Candidate:
    phrase: str
    name: str
    weeks: list[Week]
    examples: list[Example]

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.phrase).strip("-")

    @property
    def pull_request_body(self) -> str:
        weeks = ", ".join(week.label for week in self.weeks)
        examples = "\n".join(f"- {story_link(example)}" for example in self.examples)
        return (
            f"\"{self.phrase}\" rose among Hacker News story titles in {len(self.weeks)} of the last {WEEKS_LOOKED_AT} "
            f"weeks: {weeks}.\n\nThis adds {self.name} to the catalog in the rising era. Merge it to give it history and a "
            f"forecast, move it to another era first if one fits, or close it and it won't be proposed again.\n\n"
            f"Titles from those weeks:\n\n{examples}\n"
        )


def candidates(record: WeeklyWords, catalog_phrases: set[str]) -> list[Candidate]:
    looked_at = record.recorded_weeks()[-WEEKS_LOOKED_AT:]
    risen: dict[str, list[Week]] = {}
    for week in looked_at:
        for phrase in record.weeks[week].risers:
            risen.setdefault(phrase, []).append(week)
    return [
        _candidate(phrase, weeks, record)
        for phrase, weeks in risen.items()
        if len(weeks) >= LEAST_WEEKS_RISEN and phrase not in catalog_phrases
    ]


def with_candidate(catalog_source: str, candidate: Candidate) -> str:
    end = catalog_source.index(CATALOG_END, catalog_source.index(CATALOG_START))
    return catalog_source[:end] + f"\n    {_entry(candidate)}," + catalog_source[end:]


def _candidate(phrase: str, weeks: list[Week], record: WeeklyWords) -> Candidate:
    examples = [example for week in weeks for example in record.weeks[week].risers[phrase]]
    return Candidate(phrase, _usual_spelling(phrase, [title for _, title in examples]), weeks, examples)


def _usual_spelling(phrase: str, titles: list[str]) -> str:
    pattern = re.compile(r"\b" + r"\W+".join(re.escape(word) for word in phrase.split(" ")) + r"\b", re.IGNORECASE)
    spellings = Counter(found.group(0) for title in titles for found in pattern.finditer(title))
    return spellings.most_common(1)[0][0] if spellings else phrase


def _entry(candidate: Candidate) -> str:
    arguments = [candidate.name, "rising"] + ([candidate.phrase] if candidate.name.lower() != candidate.phrase else [])
    return f"_buzzword({', '.join(json.dumps(argument, ensure_ascii=False) for argument in arguments)})"
