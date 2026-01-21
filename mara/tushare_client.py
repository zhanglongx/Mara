"""Tushare client wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd
import tushare as ts


@dataclass
class TushareClient:
    token: str

    def __post_init__(self) -> None:
        ts.set_token(self.token)
        self._pro: Any = ts.pro_api(self.token)

    def query(self, api_name: str, **params: Any) -> pd.DataFrame:
        result: Any = self._pro.query(api_name, **params)
        if isinstance(result, pd.DataFrame):
            return result
        return pd.DataFrame(result)

    def stock_basic(self, fields: Iterable[str]) -> pd.DataFrame:
        fields_value: str = ",".join(fields)
        return self.query("stock_basic", fields=fields_value)
