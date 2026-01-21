"""Date utilities for mara."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date


def parse_cli_date(value: str) -> date:
    parsed: datetime = datetime.strptime(value, "%Y-%m-%d")
    return parsed.date()


def parse_yyyymmdd(value: str) -> date:
    parsed: datetime = datetime.strptime(value, "%Y%m%d")
    return parsed.date()


def to_yyyymmdd(value: date) -> str:
    return value.strftime("%Y%m%d")


def to_date_range(start: str | None, end: str | None, default_start: date) -> DateRange:
    start_date: date = parse_cli_date(start) if start else default_start
    end_date: date = parse_cli_date(end) if end else date.today()
    if end_date < start_date:
        raise ValueError("end_date must be >= start_date")
    return DateRange(start=start_date, end=end_date)


def quarter_from_date(value: date) -> int:
    if value.month in (1, 2, 3):
        return 1
    if value.month in (4, 5, 6):
        return 2
    if value.month in (7, 8, 9):
        return 3
    return 4


def is_quarter_end(value: date) -> bool:
    month_day: tuple[int, int] = (value.month, value.day)
    return month_day in ((3, 31), (6, 30), (9, 30), (12, 31))


def filter_quarter_dates(values: Iterable[date], season: int) -> list[bool]:
    results: list[bool] = []
    for item in values:
        item_date: date = item
        is_match: bool = quarter_from_date(item_date) == season and is_quarter_end(item_date)
        results.append(is_match)
    return results
