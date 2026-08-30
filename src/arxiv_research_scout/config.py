from __future__ import annotations

from typing import Any

import yaml

from arxiv_research_scout.paths import CONFIG_FILE


def load_config() -> dict[str, Any]:
    """
    Load the project configuration from config/scout.yaml.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(
            "Configuration file must contain a YAML mapping."
        )

    return config