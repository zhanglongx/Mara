"""Smoke tests for the CLI entrypoint."""

from __future__ import annotations

import argparse

import pytest

from mara.main import _build_options, build_parser, main
from mara.query_options import QueryOptions


def test_build_parser_parses_keywords() -> None:
    parser: argparse.ArgumentParser = build_parser()
    parsed: argparse.Namespace = parser.parse_args(["-i", "roe", "000001.SZ", "600000.SH"])

    assert parsed.indicators == "roe"
    assert parsed.keywords == ["000001.SZ", "600000.SH"]


def test_build_options_rejects_empty_indicators() -> None:
    parser: argparse.ArgumentParser = build_parser()
    parsed: argparse.Namespace = parser.parse_args(["-i", "roe"])
    parsed.indicators = " , "

    with pytest.raises(ValueError, match="--indicators cannot be empty"):
        _build_options(parsed)


def test_main_runs_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run_app(options: QueryOptions, keywords: list[str]) -> object:
        assert options.indicators == ["roe"]
        assert keywords == ["000001.SZ"]
        return object()

    monkeypatch.setattr("mara.main.setup_logging", lambda _level: None)
    monkeypatch.setattr("mara.main.run_app", fake_run_app)

    exit_code: int = main(["-i", "roe", "000001.SZ"])
    assert exit_code == 0
