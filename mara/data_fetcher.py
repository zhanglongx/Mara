"""Fetch indicator data from Tushare and plugins."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Iterable

import pandas as pd

from mara.constants import META_FIELDS, SINGLE_QUARTER_APIS
from mara.date_utils import DateRange, filter_quarter_dates, to_yyyymmdd
from mara.indicator_registry import IndicatorRegistry
from mara.tushare_client import TushareClient


@dataclass(frozen=True)
class IndicatorResult:
    name: str
    frequency: str
    data: pd.DataFrame


class DataFetcher:
    def __init__(self, client: TushareClient, registry: IndicatorRegistry) -> None:
        self._client: TushareClient = client
        self._registry: IndicatorRegistry = registry

    def fetch_indicators(
        self,
        indicators: Iterable[str],
        ts_codes: Iterable[str],
        date_range: DateRange | None,
        season: int,
        single: bool,
        latest: bool,
        aggregate: str | None,
    ) -> list[IndicatorResult]:
        indicator_list: list[str] = list(indicators)
        ts_code_list: list[str] = list(ts_codes)
        grouped: dict[str, list[str]] = {}
        results: list[IndicatorResult] = []

        for indicator in indicator_list:
            api_name: str | None = self._registry.get_api(indicator)
            if api_name is None:
                custom_data: pd.DataFrame = self._run_custom_indicator(
                    indicator, ts_code_list
                )
                results.append(
                    IndicatorResult(name=indicator, frequency="custom", data=custom_data)
                )
                continue
            grouped.setdefault(api_name, []).append(indicator)

        for api_name, api_indicators in grouped.items():
            api_df: pd.DataFrame = self._fetch_api_data(
                api_name,
                api_indicators,
                ts_code_list,
                date_range,
                season,
                single,
                latest,
                aggregate,
            )
            if api_df.empty:
                continue
            for indicator in api_indicators:
                meta_cols: list[str] = [col for col in META_FIELDS if col in api_df.columns]
                indicator_df: pd.DataFrame = api_df[meta_cols + [indicator]].copy()
                results.append(
                    IndicatorResult(
                        name=indicator, frequency="quarterly", data=indicator_df
                    )
                )

        return results

    def _run_custom_indicator(
        self, indicator: str, ts_code_list: list[str]
    ) -> pd.DataFrame:
        custom_func: Callable[[pd.DataFrame], pd.Series] | None = (
            self._registry.custom_indicators.get(indicator)
        )
        if custom_func is None:
            raise ValueError(f"Unknown indicator: {indicator}")
        empty_df: pd.DataFrame = pd.DataFrame({"ts_code": ts_code_list})
        series: pd.Series = custom_func(empty_df)
        custom_df: pd.DataFrame = pd.DataFrame({"ts_code": ts_code_list, indicator: series})
        return custom_df

    def _fetch_api_data(
        self,
        api_name: str,
        indicators: list[str],
        ts_codes: list[str],
        date_range: DateRange | None,
        season: int,
        single: bool,
        latest: bool,
        aggregate: str | None,
    ) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        fields: list[str] = META_FIELDS + indicators
        fields_value: str = ",".join(fields)

        for ts_code in ts_codes:
            params: dict[str, Any] = {"ts_code": ts_code, "fields": fields_value}
            if date_range is not None and not latest:
                params["start_date"] = to_yyyymmdd(date_range.start)
                params["end_date"] = to_yyyymmdd(date_range.end)
            api_df: pd.DataFrame = self._client.query(api_name, **params)
            if api_df.empty:
                continue
            frames.append(api_df)

        if not frames:
            return pd.DataFrame()

        combined_df: pd.DataFrame = pd.concat(frames, ignore_index=True)
        combined_df = self._normalize_and_filter_range(combined_df, date_range)

        if single and api_name in SINGLE_QUARTER_APIS:
            combined_df = self._to_single_quarter(combined_df, indicators)

        combined_df = self._filter_by_season(combined_df, season)

        if latest:
            combined_df = self._select_latest(combined_df)
        elif aggregate:
            combined_df = self._aggregate_quarter(combined_df, indicators, aggregate)

        return combined_df

    def _normalize_and_filter_range(
        self, data: pd.DataFrame, date_range: DateRange | None
    ) -> pd.DataFrame:
        data = data.copy()
        end_dates: pd.Series = pd.to_datetime(
            data["end_date"], format="%Y%m%d", errors="coerce"
        )
        data["_end_date"] = end_dates
        data = data[data["_end_date"].notna()]

        if date_range is not None:
            start_date: date = date_range.start
            end_date: date = date_range.end
            mask_range: pd.Series = (data["_end_date"].dt.date >= start_date) & (
                data["_end_date"].dt.date <= end_date
            )
            data = data[mask_range]

        data = data.sort_values(["ts_code", "_end_date"]).drop(columns=["_end_date"])
        data["end_date"] = data["end_date"].astype(str)
        return data

    def _filter_by_season(self, data: pd.DataFrame, season: int) -> pd.DataFrame:
        if season not in (1, 2, 3, 4):
            return data
        data = data.copy()
        data["_end_date"] = pd.to_datetime(data["end_date"], format="%Y%m%d", errors="coerce")
        data = data[data["_end_date"].notna()]
        quarter_mask: list[bool] = filter_quarter_dates(
            data["_end_date"].dt.date.tolist(), season
        )
        data = data[pd.Series(quarter_mask, index=data.index)]
        data = data.drop(columns=["_end_date"])
        return data

    def _to_single_quarter(self, data: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
        data = data.copy()
        data["_end_date"] = pd.to_datetime(data["end_date"], format="%Y%m%d", errors="coerce")
        data = data[data["_end_date"].notna()]
        data["_year"] = data["_end_date"].dt.year
        data = data.sort_values(["ts_code", "_year", "_end_date"])

        for indicator in indicators:
            data[indicator] = (
                data.groupby(["ts_code", "_year"], sort=False)[indicator]
                .diff()
                .fillna(data[indicator])
            )

        data = data.drop(columns=["_end_date", "_year"])
        return data

    def _select_latest(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data["_end_date"] = pd.to_datetime(data["end_date"], format="%Y%m%d", errors="coerce")
        data = data[data["_end_date"].notna()]
        data = data.sort_values(["ts_code", "_end_date"])
        latest_df: pd.DataFrame = data.groupby("ts_code", as_index=False).tail(1)
        latest_df = latest_df.drop(columns=["_end_date"])
        return latest_df

    def _aggregate_quarter(
        self, data: pd.DataFrame, indicators: list[str], agg: str
    ) -> pd.DataFrame:
        data = data.copy()
        grouped: Any = data.groupby("ts_code", as_index=False)[indicators]
        if agg == "mean":
            agg_df: pd.DataFrame = grouped.mean(numeric_only=True)
        else:
            agg_df: pd.DataFrame = grouped.median(numeric_only=True)
        agg_df["ann_date"] = None
        agg_df["end_date"] = None
        columns: list[str] = META_FIELDS + indicators
        return agg_df[columns]
