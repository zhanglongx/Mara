"""Indicator registry and documentation parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

from mara.constants import META_FIELDS

CustomCompute = Callable[[pd.DataFrame], pd.Series]


@dataclass
class ApiSpec:
    name: str
    fields: list[str]


@dataclass
class IndicatorSpec:
    name: str
    api: str
    is_custom: bool = False


@dataclass
class IndicatorRegistry:
    api_specs: dict[str, ApiSpec]
    indicator_to_api: dict[str, str] = field(default_factory=dict)
    custom_indicators: dict[str, CustomCompute] = field(default_factory=dict)

    def register_indicator(self, name: str, api: str) -> None:
        self.indicator_to_api[name] = api

    def register_custom_indicator(self, name: str, compute: CustomCompute) -> None:
        self.custom_indicators[name] = compute

    def get_api(self, name: str) -> str | None:
        if name in self.custom_indicators:
            return None
        return self.indicator_to_api.get(name)

    def is_custom(self, name: str) -> bool:
        return name in self.custom_indicators


def parse_api_doc(path: Path) -> ApiSpec:
    api_name: str = ""
    fields: list[str] = []
    in_output: bool = False
    lines: list[str] = path.read_text(encoding="utf-8").splitlines()

    for raw_line in lines:
        line: str = raw_line.strip()
        if not line:
            continue
        if line.startswith("接口："):
            api_name = line.split("接口：", 1)[1].split("，", 1)[0].strip()
            continue
        if line.startswith("输出参数"):
            in_output = True
            continue
        if not in_output:
            continue
        if line.startswith("名称"):
            continue
        cols: list[str] = line.split("\t")
        if not cols:
            continue
        field_name: str = cols[0].strip()
        if field_name:
            fields.append(field_name)

    if not api_name:
        raise ValueError(f"No api name found in {path}")
    return ApiSpec(name=api_name, fields=fields)


def load_registry(doc_dir: Path, api_order: Iterable[str]) -> IndicatorRegistry:
    api_specs: dict[str, ApiSpec] = {}
    doc_paths: list[Path] = list(doc_dir.glob("api_*.txt"))
    for doc_path in doc_paths:
        api_spec: ApiSpec = parse_api_doc(doc_path)
        api_specs[api_spec.name] = api_spec

    registry: IndicatorRegistry = IndicatorRegistry(api_specs=api_specs)
    ordered_apis: list[str] = list(api_order)

    for api_name in ordered_apis:
        api_spec: ApiSpec | None = api_specs.get(api_name)
        if not api_spec:
            continue
        for field_name in api_spec.fields:
            if field_name in META_FIELDS:
                continue
            if field_name not in registry.indicator_to_api:
                registry.register_indicator(field_name, api_name)

    return registry
