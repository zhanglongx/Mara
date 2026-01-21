"""Indicator registry with embedded API specs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

import pandas as pd

from mara.constants import EMBEDDED_API_FIELDS, META_FIELDS

CustomCompute = Callable[[pd.DataFrame], pd.Series]


@dataclass
class ApiSpec:
    name: str
    fields: list[str]


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

def load_registry(api_order: Iterable[str]) -> IndicatorRegistry:
    api_specs: dict[str, ApiSpec] = _build_api_specs()
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


def _build_api_specs() -> dict[str, ApiSpec]:
    api_specs: dict[str, ApiSpec] = {}
    for api_name, fields in EMBEDDED_API_FIELDS.items():
        field_names: list[str] = [field_name for field_name, _cn_name in fields]
        api_specs[api_name] = ApiSpec(name=api_name, fields=field_names)
    return api_specs
