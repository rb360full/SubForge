"""Logging infrastructure for SubForge."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Logger configuration."""

    level: str = "INFO"
    log_file: Path | None = None


class LoggingManager:
    """Factory for reusable application loggers."""

    def __init__(self, config: LoggingConfig) -> None:
        self._config = config

    def configure(self, logger_name: str = "subforge") -> logging.Logger:
        logger = logging.getLogger(logger_name)
        logger.setLevel(self._resolve_level(self._config.level))
        logger.handlers.clear()
        logger.propagate = False

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if self._config.log_file is not None:
            self._config.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self._config.log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def _resolve_level(self, level_name: str) -> int:
        level = logging.getLevelName(level_name.upper())
        if isinstance(level, int):
            return level
        return logging.INFO

