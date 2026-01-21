"""Main application workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from mara.config import AppConfig, load_config
from mara.constants import API_ORDER
from mara.data_fetcher import DataFetcher, IndicatorResult
from mara.data_processor import DataProcessor, OutputTable
from mara.date_utils import DateRange, to_date_range
from mara.excel_exporter import ExcelExporter
from mara.indicator_registry import IndicatorRegistry, load_registry
from mara.plugin_loader import load_plugins
from mara.query_options import QueryOptions
from mara.stock_selector import StockSelection, select_stocks
from mara.tushare_client import TushareClient
from mara.output import print_tables
from mara.plotter import plot_indicators


@dataclass(frozen=True)
class AppResult:
    tables: list[OutputTable]
    indicators: list[IndicatorResult]


def run_app(options: QueryOptions, keywords: Iterable[str]) -> AppResult:
    _validate_options(options)

    config: AppConfig = load_config(options.config_path)
    client: TushareClient = TushareClient(token=config.token)

    registry: IndicatorRegistry = load_registry(API_ORDER)
    plugin_dir: Path = Path.cwd() / "plugins"
    load_plugins(plugin_dir, registry)

    selection: StockSelection = select_stocks(client, keywords)
    if not selection.ts_codes:
        return AppResult(tables=[], indicators=[])

    date_range: DateRange | None = None
    if not options.latest:
        date_range = to_date_range(
            options.start_date, options.end_date, default_start=_default_start()
        )

    data_fetcher: DataFetcher = DataFetcher(client=client, registry=registry)
    results: list[IndicatorResult] = data_fetcher.fetch_indicators(
        indicators=options.indicators,
        ts_codes=selection.ts_codes,
        date_range=date_range,
        season=options.season,
        single=options.single,
        latest=options.latest,
        aggregate=options.aggregate,
    )

    include_end_date: bool = not options.latest and options.aggregate is None
    data_processor: DataProcessor = DataProcessor(selection.basic_info)
    tables: list[OutputTable] = data_processor.build_output_tables(
        results, include_end_date
    )

    if options.sort_by:
        _sort_tables(tables, options.sort_by, options.sort_order)

    print_tables(tables, options.delimiter, include_header=not options.no_header)

    if options.excel_path:
        excel_exporter: ExcelExporter = ExcelExporter(selection.basic_info)
        excel_exporter.export(options.excel_path, results)

    if options.plot:
        plot_indicators(results)

    return AppResult(tables=tables, indicators=results)


def _default_start() -> date:
    return date(2020, 1, 1)


def _validate_options(options: QueryOptions) -> None:
    if options.latest and options.aggregate:
        raise ValueError("--latest and --aggregate cannot be used together")
    if options.aggregate and options.season not in (1, 2, 3, 4):
        raise ValueError("--aggregate requires a valid --season")


# TODO: take effort
def _sort_tables(tables: list[OutputTable], sort_by: str, order: str) -> None:
    descending: bool = order == "desc"
    for table in tables:
        if sort_by in table.data.columns:
            has_end_date: bool = "end_date" in table.data.columns and bool(
                table.data["end_date"].notna().any()
            )
            if has_end_date:
                continue
            table.data.sort_values(sort_by, ascending=not descending, inplace=True)
