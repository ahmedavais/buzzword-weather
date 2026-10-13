from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class Month:
    year: int
    month: int

    @property
    def starts_at(self) -> int:
        return _timestamp(self.year, self.month)

    @property
    def ends_at(self) -> int:
        following = self.next()
        return _timestamp(following.year, following.month)

    @property
    def label(self) -> str:
        return date(self.year, self.month, 1).strftime("%b %Y")

    def next(self) -> "Month":
        return Month(self.year + 1, 1) if self.month == 12 else Month(self.year, self.month + 1)

    def previous(self) -> "Month":
        return Month(self.year - 1, 12) if self.month == 1 else Month(self.year, self.month - 1)


def months_ending(day: date, count: int) -> list[Month]:
    months = [Month(day.year, day.month)]
    while len(months) < count:
        months.insert(0, months[0].previous())
    return months


def _timestamp(year: int, month: int) -> int:
    return int(datetime(year, month, 1, tzinfo=timezone.utc).timestamp())
