"""Configuration loading for mara."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    token: str


def load_config(path: str) -> AppConfig:
    config_path: Path = Path(path).expanduser()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw_text: str = config_path.read_text(encoding="utf-8")
    raw_data: Any = yaml.safe_load(raw_text)
    if not isinstance(raw_data, dict):
        raise ValueError("Config file must contain a YAML mapping")

    token_value: Any = raw_data.get("token")
    if not isinstance(token_value, str) or not token_value.strip():
        raise ValueError("Config file must contain a non-empty 'token'")

    return AppConfig(token=token_value.strip())
