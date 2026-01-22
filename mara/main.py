"""CLI entrypoint for mara."""

from __future__ import annotations

import argparse

from mara.app import run_app
from mara.query_options import QueryOptions


def build_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="mara", description="Stock analysis CLI via Tushare"
    )
    parser.add_argument("keywords", nargs="*", help="Stock codes/names/industry keywords")
    parser.add_argument("-i", "--indicators", required=True, help="Indicators, comma-separated")
    parser.add_argument("-s", "--start-date", dest="start_date", help="YYYY-MM-DD")
    parser.add_argument("-e", "--end-date", dest="end_date", help="YYYY-MM-DD")
    parser.add_argument("--season", type=int, choices=[1, 2, 3, 4], default=4)
    parser.add_argument("--single", action="store_true", help="Use single-quarter (non-cumulative) values")
    parser.add_argument("--latest", action="store_true", help="Fetch latest data")
    parser.add_argument("-a", "--aggregate", choices=["mean", "median"], help="Aggregate quarterly data")
    parser.add_argument("-t", "--sort-by", dest="sort_by", help="Sort by indicator")
    parser.add_argument("--sort-order", choices=["asc", "desc"], default="asc")
    parser.add_argument("-x", "--excel", dest="excel_path", help="Excel output path")
    parser.add_argument("--no-header", action="store_true", help="Disable header row")
    parser.add_argument("--delimiter", default=",", help="Output delimiter")
    parser.add_argument("-p", "--plot", action="store_true", help="Plot indicators")
    parser.add_argument("-c", "--config", dest="config_path", default="~/.mararc")
    parser.add_argument("--version", action="version", version="mara 0.1.0")
    parser.add_argument("--debug", action="store_true")
    return parser


def _build_options(parsed: argparse.Namespace) -> QueryOptions:
    indicators_value: str = parsed.indicators
    indicators: list[str] = [item.strip() for item in indicators_value.split(",") if item.strip()]
    if not indicators:
        raise ValueError("--indicators cannot be empty")
    options: QueryOptions = QueryOptions(
        indicators=indicators,
        start_date=parsed.start_date,
        end_date=parsed.end_date,
        season=parsed.season,
        single=parsed.single,
        latest=parsed.latest,
        aggregate=parsed.aggregate,
        sort_by=parsed.sort_by,
        sort_order=parsed.sort_order,
        no_header=parsed.no_header,
        delimiter=parsed.delimiter,
        plot=parsed.plot,
        excel_path=parsed.excel_path,
        config_path=parsed.config_path,
        debug=parsed.debug,
    )
    return options


def main(argv: list[str] | None = None) -> int:
    parser: argparse.ArgumentParser = build_parser()
    parsed: argparse.Namespace = parser.parse_args(argv)
    options: QueryOptions = _build_options(parsed)
    keywords: list[str] = list(parsed.keywords)
    _ = run_app(options, keywords)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
