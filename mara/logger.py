"""Logging utilities for mara."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Final

LOGGER_NAME: Final[str] = "mara"
DEFAULT_LOG_LEVEL_NAME: Final[str] = "warn"
LOG_LEVEL_CHOICES: Final[tuple[str, ...]] = ("error", "warn", "info", "debug")
LOG_LEVEL_ALIASES: Final[dict[str, int]] = {
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def parse_log_level(raw: str) -> int:
    value: str = raw.strip().lower()
    level: int | None = LOG_LEVEL_ALIASES.get(value)
    if level is None:
        choices: str = ", ".join(LOG_LEVEL_CHOICES)
        raise argparse.ArgumentTypeError(
            f"Invalid log level '{raw}'. Choose from: {choices}"
        )
    return level


def setup_logging(level: int) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        handler: logging.StreamHandler = logging.StreamHandler(stream=sys.stderr)
        handler.setLevel(level)
        formatter: logging.Formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            handler.setLevel(level)
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
