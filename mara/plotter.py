"""Plotting utilities for mara."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

from mara.data_fetcher import IndicatorResult


@dataclass(frozen=True)
class PlotSpec:
    title: str
    data: pd.DataFrame
    indicator: str


def plot_indicators(results: Iterable[IndicatorResult]) -> None:
    specs: list[PlotSpec] = []
    for result in results:
        if result.data.empty:
            continue
        specs.append(PlotSpec(title=result.name, data=result.data, indicator=result.name))

    if not specs:
        return

    fig: plt.Figure
    axes: list[plt.Axes] | plt.Axes
    fig, axes = plt.subplots(len(specs), 1, figsize=(10, 4 * len(specs)))
    if len(specs) == 1:
        axes = [axes]

    for axis, spec in zip(axes, specs):
        _plot_indicator(axis, spec)

    plt.tight_layout()
    plt.show()


def _plot_indicator(axis: plt.Axes, spec: PlotSpec) -> None:
    data: pd.DataFrame = spec.data.copy()
    if "end_date" in data.columns and data["end_date"].notna().any():
        data["_end_date"] = pd.to_datetime(data["end_date"], format="%Y%m%d", errors="coerce")
        for ts_code, group in data.groupby("ts_code"):
            group_sorted: pd.DataFrame = group.sort_values("_end_date")
            axis.plot(group_sorted["_end_date"], group_sorted[spec.indicator], label=ts_code)
        axis.set_xlabel("Date")
        axis.set_ylabel(spec.indicator)
    else:
        axis.bar(data["ts_code"].astype(str), data[spec.indicator])
        axis.set_xlabel("TS Code")
        axis.set_ylabel(spec.indicator)

    axis.set_title(spec.title)
    axis.legend(loc="best", fontsize="small")
