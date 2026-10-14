from dataclasses import dataclass
from datetime import UTC, date, datetime


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

    @property
    def key(self) -> str:
        return f"{self.year}-{self.month:02d}"

    def next(self) -> "Month":
        return Month(self.year + 1, 1) if self.month == 12 else Month(self.year, self.month + 1)

    def previous(self) -> "Month":
        return Month(self.year - 1, 12) if self.month == 1 else Month(self.year, self.month - 1)


@dataclass(frozen=True)
class Quarter:
    year: int
    quarter: int

    @property
    def first_month(self) -> Month:
        return Month(self.year, 3 * self.quarter - 2)

    @property
    def starts_at(self) -> int:
        return self.first_month.starts_at

    @property
    def ends_at(self) -> int:
        return self.next().starts_at

    @property
    def label(self) -> str:
        return f"Q{self.quarter} {self.year}"

    @property
    def key(self) -> str:
        return f"{self.year}-Q{self.quarter}"

    def next(self) -> "Quarter":
        return Quarter(self.year + 1, 1) if self.quarter == 4 else Quarter(self.year, self.quarter + 1)

    def previous(self) -> "Quarter":
        return Quarter(self.year - 1, 4) if self.quarter == 1 else Quarter(self.year, self.quarter - 1)


Period = Month | Quarter


def quarter_of(day: date) -> Quarter:
    return Quarter(day.year, (day.month - 1) // 3 + 1)


def complete_quarters_before(day: date, count: int) -> list[Quarter]:
    quarters = [quarter_of(day).previous()]
    while len(quarters) < count:
        quarters.insert(0, quarters[0].previous())
    return quarters


def complete_quarters_since(first_year: int, before: date) -> list[Quarter]:
    quarters = [Quarter(first_year, 1)]
    in_progress = quarter_of(before)
    while quarters[-1].next() != in_progress:
        quarters.append(quarters[-1].next())
    return quarters


def months_ending(day: date, count: int) -> list[Month]:
    months = [Month(day.year, day.month)]
    while len(months) < count:
        months.insert(0, months[0].previous())
    return months


def complete_months_before(day: date, count: int) -> list[Month]:
    last_complete = Month(day.year, day.month).previous()
    return months_ending(date(last_complete.year, last_complete.month, 1), count)


def _timestamp(year: int, month: int) -> int:
    return int(datetime(year, month, 1, tzinfo=UTC).timestamp())
