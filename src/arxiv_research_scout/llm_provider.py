from __future__ import annotations

import os
from collections.abc import Mapping

from openai import OpenAI

from arxiv_research_scout.models import (
    LLMProviderSettings,
)


VALID_PROVIDERS = {
    "openai",
    "deepseek",
}


API_KEY_ENVIRONMENTS = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


def normalize_provider(
    provider: str,
) -> str:
    """
    Normalize and validate an LLM provider name.
    """

    normalized = provider.strip().lower()

    if normalized not in VALID_PROVIDERS:
        raise ValueError(
            "Unsupported LLM provider: "
            f"{provider}. "
            "Expected one of: "
            f"{sorted(VALID_PROVIDERS)}"
        )

    return normalized


def resolve_provider_settings(
    config: dict,
    *,
    provider_override: str | None = None,
    model_override: str | None = None,
) -> LLMProviderSettings:
    """
    Resolve runtime LLM settings.

    Command-line overrides take precedence over
    values stored in config/scout.yaml.
    """

    llm_config = config["llm"]

    provider = normalize_provider(
        provider_override
        or llm_config["default_provider"]
    )

    provider_config = llm_config.get(
        provider
    )

    if not isinstance(
        provider_config,
        dict,
    ):
        raise ValueError(
            f"Missing configuration for "
            f"provider: {provider}"
        )

    if model_override is not None:
        model = model_override.strip()
    else:
        model = str(
            provider_config.get(
                "model",
                "",
            )
        ).strip()

    if not model:
        raise ValueError(
            f"No model configured for "
            f"provider: {provider}"
        )

    max_output_tokens = int(
        llm_config.get(
            "max_output_tokens",
            2500,
        )
    )

    if max_output_tokens < 1:
        raise ValueError(
            "llm.max_output_tokens must "
            "be at least 1."
        )

    base_url_value = provider_config.get(
        "base_url"
    )

    base_url = (
        str(base_url_value).strip()
        if base_url_value
        else None
    )

    return LLMProviderSettings(
        provider=provider,
        model=model,
        api_key_env=(
            API_KEY_ENVIRONMENTS[
                provider
            ]
        ),
        base_url=base_url,
        max_output_tokens=max_output_tokens,
    )


def load_provider_api_key(
    settings: LLMProviderSettings,
    *,
    environ: Mapping[str, str] | None = None,
) -> str:
    """
    Load the provider API key from the environment.

    API keys are never read from project config files.
    """

    environment = (
        os.environ
        if environ is None
        else environ
    )

    api_key = environment.get(
        settings.api_key_env,
        "",
    ).strip()

    if not api_key:
        raise RuntimeError(
            f"Environment variable "
            f"{settings.api_key_env} "
            "is not configured."
        )

    return api_key


def create_provider_client(
    settings: LLMProviderSettings,
    *,
    api_key: str,
) -> OpenAI:
    """
    Create an OpenAI-compatible client.

    OpenAI uses the SDK's default base URL.

    DeepSeek uses:
        https://api.deepseek.com
    """

    kwargs = {
        "api_key": api_key,
    }

    if settings.base_url:
        kwargs["base_url"] = (
            settings.base_url
        )

    return OpenAI(
        **kwargs
    )