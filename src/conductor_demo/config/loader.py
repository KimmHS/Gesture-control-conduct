from __future__ import annotations

import logging

from conductor_demo.config.defaults import AppConfig


LOGGER = logging.getLogger(__name__)


def load_config(config_path: str | None = None) -> AppConfig:
    """Return default config for now.

    The path argument is reserved for a later external config loader.
    """
    if config_path:
        LOGGER.info("Ignoring config path for now: %s", config_path)
    return AppConfig()
