"""Stock selection by keywords."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from mara.constants import BASIC_FIELDS
from mara.tushare_client import TushareClient


@dataclass(frozen=True)
class StockSelection:
    ts_codes: list[str]
    basic_info: pd.DataFrame


def select_stocks(client: TushareClient, keywords: Iterable[str]) -> StockSelection:
    basic_df: pd.DataFrame = client.stock_basic(fields=BASIC_FIELDS)
    if basic_df.empty:
        return StockSelection(ts_codes=[], basic_info=basic_df)

    keyword_list: list[str] = [item.strip() for item in keywords if item.strip()]
    if not keyword_list:
        ts_codes: list[str] = sorted(basic_df["ts_code"].dropna().unique().tolist())
        return StockSelection(ts_codes=ts_codes, basic_info=basic_df)

    mask: pd.Series = pd.Series(False, index=basic_df.index)
    for keyword in keyword_list:
        industry_match: pd.Series = basic_df["industry"].fillna("") == keyword
        code_match: pd.Series = basic_df["ts_code"].fillna("").str.contains(keyword, case=False)
        name_match: pd.Series = basic_df["name"].fillna("").str.contains(keyword, case=False)
        mask |= industry_match | code_match | name_match

    filtered_df: pd.DataFrame = basic_df[mask].copy()
    ts_codes: list[str] = sorted(filtered_df["ts_code"].dropna().unique().tolist())
    return StockSelection(ts_codes=ts_codes, basic_info=filtered_df)
