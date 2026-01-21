"""Combine indicator data and prepare output frames."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from mara.constants import BASIC_FIELDS, META_FIELDS
from mara.data_fetcher import IndicatorResult


@dataclass(frozen=True)
class OutputTable:
    frequency: str
    data: pd.DataFrame


def build_output_tables(
    basic_info: pd.DataFrame,
    results: Iterable[IndicatorResult],
    include_end_date: bool,
) -> list[OutputTable]:
    results_list: list[IndicatorResult] = list(results)
    if not results_list:
        return []

    tables: list[OutputTable] = []
    grouped: dict[str, list[IndicatorResult]] = {}
    for result in results_list:
        grouped.setdefault(result.frequency, []).append(result)

    for frequency, group_results in grouped.items():
        table_df: pd.DataFrame = _merge_results(group_results, include_end_date)
        table_df = _attach_basic_info(basic_info, table_df)
        tables.append(OutputTable(frequency=frequency, data=table_df))

    return tables


def _merge_results(results: list[IndicatorResult], include_end_date: bool) -> pd.DataFrame:
    base_result: IndicatorResult = max(results, key=lambda item: len(item.data))
    base_df: pd.DataFrame = base_result.data.copy()
    join_keys: list[str] = ["ts_code"]
    if include_end_date and "end_date" in base_df.columns:
        join_keys.append("end_date")

    merged: pd.DataFrame = base_df
    for result in results:
        if result is base_result:
            continue
        other_df: pd.DataFrame = result.data.copy()
        if include_end_date and "end_date" in other_df.columns and "end_date" in merged.columns:
            keys: list[str] = join_keys
        else:
            keys: list[str] = ["ts_code"]
        merged = merged.merge(other_df, on=keys, how="left")

    return merged


def _attach_basic_info(basic_info: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
    if basic_info.empty:
        return data

    info_cols: list[str] = [col for col in BASIC_FIELDS if col in basic_info.columns]
    info_df: pd.DataFrame = basic_info[info_cols].copy()
    merged: pd.DataFrame = info_df.merge(data, on="ts_code", how="right")

    ordered_cols: list[str] = []
    for col in BASIC_FIELDS:
        if col in merged.columns:
            ordered_cols.append(col)
    for col in META_FIELDS:
        if col in merged.columns and col not in ordered_cols:
            ordered_cols.append(col)
    for col in merged.columns:
        if col not in ordered_cols:
            ordered_cols.append(col)

    return merged[ordered_cols]
