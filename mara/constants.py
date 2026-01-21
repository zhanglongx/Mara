"""Shared constants."""

from __future__ import annotations

API_ORDER: list[str] = ["fina_indicator", "income", "balancesheet", "cashflow"]

SINGLE_QUARTER_APIS: set[str] = {"income", "cashflow"}

BASIC_FIELDS: list[str] = ["ts_code", "name", "industry", "market", "area", "list_date"]

META_FIELDS: list[str] = ["ts_code", "ann_date", "end_date"]
