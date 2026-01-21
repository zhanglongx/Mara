"""Stdout formatting for mara."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from mara.data_processor import OutputTable


def print_tables(tables: Iterable[OutputTable], delimiter: str, include_header: bool) -> None:
    tables_list: list[OutputTable] = list(tables)
    multiple: bool = len(tables_list) > 1

    for idx, table in enumerate(tables_list):
        if multiple:
            label: str = f"# frequency: {table.frequency}"
            print(label)
        df: pd.DataFrame = table.data
        if df.empty:
            print("")
        else:
            text: str = df.to_csv(sep=delimiter, index=False, header=include_header)
            print(text.rstrip("\n"))
        if idx < len(tables_list) - 1:
            print("")
