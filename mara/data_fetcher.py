"""Fetch indicator data from Tushare and plugins."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Iterable

import pandas as pd

from mara.constants import META_FIELDS, SINGLE_QUARTER_APIS
from mara.date_utils import DateRange, filter_quarter_dates, to_yyyymmdd
from mara.indicator_registry import ApiSpec, IndicatorRegistry
from mara.logger import get_logger
from mara.tushare_client import TushareClient

REPORT_TYPE_PRIORITY: dict[str, int] = {
    "4": 60,
    "1": 50,
    "5": 40,
    "11": 40,
    "3": 30,
    "2": 20,
    "9": 15,
    "10": 14,
    "12": 13,
    "8": 12,
    "7": 11,
    "6": 10,
}

DEDUP_FIELD_CANDIDATES: list[str] = ["report_type", "update_flag", "f_ann_date"]

LOGGER: logging.Logger = get_logger(__name__)


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
        '''
        Fetch financial indicators for multiple securities within a specified date range.
        
        This method retrieves indicator data from Tushare APIs and custom indicators.
        It organizes requests by API endpoint to minimize network calls, handles custom
        indicators separately, and applies filtering/aggregation based on user parameters.
        '''
        indicator_list: list[str] = list(indicators)
        ts_code_list: list[str] = list(ts_codes)
        grouped: dict[str, list[str]] = {}
        unsupported_single_apis: set[str] = set()
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
            if single and api_name not in SINGLE_QUARTER_APIS:
                unsupported_single_apis.add(api_name)

        if single and unsupported_single_apis:
            supported: str = ", ".join(sorted(SINGLE_QUARTER_APIS))
            ignored: str = ", ".join(sorted(unsupported_single_apis))
            LOGGER.warning(
                "--single only applies to APIs [%s]; ignored for indicators from APIs [%s]",
                supported,
                ignored,
            )

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
        dedupe_fields: list[str] = self._dedupe_fields_for_api(api_name)
        fields: list[str] = list(dict.fromkeys(META_FIELDS + dedupe_fields + indicators))
        fields_value: str = ",".join(fields)

        for ts_code in ts_codes:
            params: dict[str, Any] = {"ts_code": ts_code, "fields": fields_value}
            if date_range is not None and not latest:
                params["start_date"] = to_yyyymmdd(date_range.start)
                params["end_date"] = to_yyyymmdd(date_range.end)
            api_df: pd.DataFrame = self._client.query(api_name, **params)
            # XXX: pd complains: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated
            api_df = api_df.dropna(how="all")
            if api_df.empty:
                continue
            all_na_mask: pd.Series = api_df.isna().all()
            all_na_cols: list[str] = all_na_mask[all_na_mask].index.tolist()
            if all_na_cols:
                api_df = api_df.drop(columns=all_na_cols)
            required_cols: set[str] = {"ts_code", "end_date"}
            if not required_cols.issubset(api_df.columns):
                continue
            frames.append(api_df)

        if not frames:
            return pd.DataFrame()

        combined_df: pd.DataFrame = pd.concat(frames, ignore_index=True)
        combined_df = self._normalize_and_filter_range(combined_df, date_range)
        combined_df = self._ensure_indicator_columns(combined_df, indicators)

        if single and api_name in SINGLE_QUARTER_APIS:
            combined_df = self._to_single_quarter(combined_df, indicators)

        combined_df = self._filter_by_season(combined_df, season)

        if latest:
            combined_df = self._select_latest(combined_df)
        elif aggregate:
            combined_df = self._aggregate_quarter(combined_df, indicators, aggregate)

        return combined_df

    def _ensure_indicator_columns(
        self, data: pd.DataFrame, indicators: list[str]
    ) -> pd.DataFrame:
        missing: list[str] = [
            indicator for indicator in indicators if indicator not in data.columns
        ]
        if not missing:
            return data
        data = data.copy()
        for indicator in missing:
            data[indicator] = float("nan")
        return data

    def _dedupe_fields_for_api(self, api_name: str) -> list[str]:
        api_spec: ApiSpec | None = self._registry.api_specs.get(api_name)
        if api_spec is None:
            return []
        return [field for field in DEDUP_FIELD_CANDIDATES if field in api_spec.fields]

    def _normalize_and_filter_range(
        self, data: pd.DataFrame, date_range: DateRange | None
    ) -> pd.DataFrame:
        data = data.copy()
        end_dates: pd.Series = pd.to_datetime(
            data["end_date"], format="%Y%m%d", errors="coerce"
        )
        # FIXME: no silent failures
        data["_end_date"] = end_dates
        data = data[data["_end_date"].notna()]

        if date_range is not None:
            start_date: date = date_range.start
            end_date: date = date_range.end
            mask_range: pd.Series = (data["_end_date"].dt.date >= start_date) & ( # type: ignore
                data["_end_date"].dt.date <= end_date                             # type: ignore
            )
            data = data[mask_range]

        data = self._dedupe_by_official_fields(data)
        data = data.sort_values(["ts_code", "_end_date"]).drop(columns=["_end_date"])
        data["end_date"] = data["end_date"].astype(str)
        return data

    def _dedupe_by_official_fields(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        Deduplicate DataFrame records based on official fields (ts_code and end_date).
        This method removes duplicate records for the same security (ts_code) and reporting period (end_date),
        keeping only the most recent or highest-priority record based on multiple ranking criteria.
        The deduplication logic prioritizes records in the following order:
        1. Report type priority (defined by REPORT_TYPE_PRIORITY mapping)
        2. Update flag (preferring updated records marked as '1')
        3. Announcement date (preferring f_ann_date, then ann_date, then end_date)
        '''
        if "ts_code" not in data.columns or "end_date" not in data.columns:
            return data
        data = data.copy()
        if "_end_date" not in data.columns:
            data["_end_date"] = pd.to_datetime(
                data["end_date"], format="%Y%m%d", errors="coerce"
            )
        data = data[data["_end_date"].notna()]

        if "report_type" in data.columns:
            report_rank: pd.Series = (
                data["report_type"]
                .astype(str)
                .map(REPORT_TYPE_PRIORITY)
                .fillna(0)
                .astype(int)
            )
            data["_report_rank"] = report_rank
        else:
            data["_report_rank"] = 0

        if "update_flag" in data.columns:
            data["_update_rank"] = data["update_flag"].astype(str).eq("1").astype(int)
        else:
            data["_update_rank"] = 0

        f_ann_date: pd.Series | None = None
        if "f_ann_date" in data.columns:
            data["_f_ann_date"] = pd.to_datetime(
                data["f_ann_date"], format="%Y%m%d", errors="coerce"
            )
            f_ann_date = data["_f_ann_date"]
        ann_date: pd.Series | None = None
        if "ann_date" in data.columns:
            data["_ann_date"] = pd.to_datetime(
                data["ann_date"], format="%Y%m%d", errors="coerce"
            )
            ann_date = data["_ann_date"]

        if f_ann_date is not None:
            date_rank: pd.Series = f_ann_date
            if ann_date is not None:
                date_rank = date_rank.fillna(ann_date)
        elif ann_date is not None:
            date_rank = ann_date
        else:
            date_rank = data["_end_date"]

        data["_date_rank"] = date_rank.fillna(data["_end_date"])
        data = data.sort_values(
            ["ts_code", "_end_date", "_report_rank", "_update_rank", "_date_rank"]
        )
        data = data.groupby(["ts_code", "_end_date"], as_index=False, sort=False).tail(1)
        drop_cols: list[str] = [
            "_report_rank",
            "_update_rank",
            "_date_rank",
            "_ann_date",
            "_f_ann_date",
        ]
        data = data.drop(columns=[col for col in drop_cols if col in data.columns])
        return data

    def _filter_by_season(self, data: pd.DataFrame, season: int) -> pd.DataFrame:
        if season == 0:
            return data
        if season not in (1, 2, 3, 4):
            return data
        data = data.copy()
        data["_end_date"] = pd.to_datetime(data["end_date"], format="%Y%m%d", errors="coerce")
        data = data[data["_end_date"].notna()]
        quarter_mask: list[bool] = filter_quarter_dates(
            data["_end_date"].dt.date.tolist(), season # type: ignore
        )
        data = data[pd.Series(quarter_mask, index=data.index)]
        data = data.drop(columns=["_end_date"])
        return data

    def _to_single_quarter(self, data: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
        data = data.copy()
        data["_end_date"] = pd.to_datetime(data["end_date"], format="%Y%m%d", errors="coerce")
        data = data[data["_end_date"].notna()]
        data["_year"] = data["_end_date"].dt.year # type: ignore
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
        elif agg == "median":
            agg_df: pd.DataFrame = grouped.median(numeric_only=True)
        else:
            raise ValueError(f"Unsupported aggregate method: {agg}")
        agg_df["ann_date"] = None
        agg_df["end_date"] = None
        columns: list[str] = META_FIELDS + indicators
        return agg_df[columns]
