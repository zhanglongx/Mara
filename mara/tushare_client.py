"""Tushare client wrapper."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd
import tushare as ts


@dataclass
class TushareClient:
    token: str
    max_retries: int = 3
    retry_delay: float = 60.0

    def __post_init__(self) -> None:
        self._pro: Any = ts.pro_api(self.token)

    def query(self, api_name: str, **params: Any) -> pd.DataFrame:
        attempt: int = 0
        while True:
            try:
                result: Any = self._pro.query(api_name, **params)
                if isinstance(result, pd.DataFrame):
                    return result
                return pd.DataFrame(result)
            except Exception:
                attempt += 1
                if attempt > self.max_retries:
                    raise
                time.sleep(self.retry_delay)

    def stock_basic(self, fields: Iterable[str]) -> pd.DataFrame:
        fields_value: str = ",".join(fields)
        return self.query("stock_basic", fields=fields_value)
