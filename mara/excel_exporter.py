"""Excel export handling."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from mara.constants import BASIC_FIELDS, META_FIELDS
from mara.data_fetcher import IndicatorResult


@dataclass(frozen=True)
class ExcelSheet:
    name: str
    data: pd.DataFrame


class ExcelExporter:
    def __init__(self, basic_info: pd.DataFrame) -> None:
        self._basic_info: pd.DataFrame = basic_info

    def export(self, path: str, results: Iterable[IndicatorResult]) -> None:
        output_path: Path = Path(path).expanduser()
        sheets: list[ExcelSheet] = self._build_sheets(list(results))
        if not sheets:
            return

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet in sheets:
                sheet.data.to_excel(writer, sheet_name=sheet.name, index=False)

    def _build_sheets(self, results: list[IndicatorResult]) -> list[ExcelSheet]:
        sheets: list[ExcelSheet] = []
        used_names: dict[str, int] = {}
        for result in results:
            df: pd.DataFrame = self._attach_basic_info(result.data)
            base_name: str = self._sanitize_sheet_name(result.name)
            sheet_name: str = self._dedupe_sheet_name(base_name, used_names)
            sheets.append(ExcelSheet(name=sheet_name, data=df))
        return sheets

    def _attach_basic_info(self, data: pd.DataFrame) -> pd.DataFrame:
        if self._basic_info.empty:
            return data

        info_cols: list[str] = [col for col in BASIC_FIELDS if col in self._basic_info.columns]
        info_df: pd.DataFrame = self._basic_info[info_cols].copy()
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

    def _sanitize_sheet_name(self, name: str) -> str:
        cleaned: str = name.replace("/", "_")
        if len(cleaned) > 31:
            cleaned = cleaned[:31]
        if not cleaned:
            cleaned = "sheet"
        return cleaned

    def _dedupe_sheet_name(self, base: str, used: dict[str, int]) -> str:
        if base not in used:
            used[base] = 1
            return base
        used[base] += 1
        suffix: str = f"_{used[base]}"
        truncated: str = base
        if len(base) + len(suffix) > 31:
            truncated = base[: 31 - len(suffix)]
        return f"{truncated}{suffix}"
