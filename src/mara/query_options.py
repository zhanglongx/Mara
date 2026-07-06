"""Query options derived from CLI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryOptions:
    indicators: list[str]
    start_date: str | None
    end_date: str | None
    season: int
    single: bool
    latest: bool
    aggregate: str | None
    sort_by: str | None
    sort_order: str
    no_header: bool
    delimiter: str
    plot: bool
    excel_path: str | None
    config_path: str
    log_level: int
    debug: bool
