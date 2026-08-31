import pytest

from arxiv_research_scout.llm_provider import (
    load_provider_api_key,
    normalize_provider,
    resolve_provider_settings,
)


def make_config() -> dict:
    return {
        "llm": {
            "default_provider": "openai",
            "max_output_tokens": 2500,
            "openai": {
                "model": "gpt-5.6-terra",
            },
            "deepseek": {
                "model": "deepseek-v4-pro",
                "base_url": (
                    "https://api.deepseek.com"
                ),
            },
        }
    }


def test_default_provider_is_used() -> None:
    settings = resolve_provider_settings(
        make_config()
    )

    assert settings.provider == "openai"

    assert settings.model == (
        "gpt-5.6-terra"
    )

    assert settings.api_key_env == (
        "OPENAI_API_KEY"
    )

    assert settings.base_url is None


def test_provider_override_is_used() -> None:
    settings = resolve_provider_settings(
        make_config(),
        provider_override="deepseek",
    )

    assert settings.provider == (
        "deepseek"
    )

    assert settings.model == (
        "deepseek-v4-pro"
    )

    assert settings.api_key_env == (
        "DEEPSEEK_API_KEY"
    )

    assert settings.base_url == (
        "https://api.deepseek.com"
    )


def test_provider_is_case_insensitive() -> None:
    assert normalize_provider(
        "DeepSeek"
    ) == "deepseek"


def test_invalid_provider_is_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_provider(
            "unknown-provider"
        )


def test_model_override_is_used() -> None:
    settings = resolve_provider_settings(
        make_config(),
        provider_override="openai",
        model_override="gpt-test-model",
    )

    assert settings.model == (
        "gpt-test-model"
    )


def test_api_key_is_loaded_from_environment() -> None:
    settings = resolve_provider_settings(
        make_config(),
        provider_override="deepseek",
    )

    api_key = load_provider_api_key(
        settings,
        environ={
            "DEEPSEEK_API_KEY": (
                "test-secret-key"
            ),
        },
    )

    assert api_key == (
        "test-secret-key"
    )


def test_missing_api_key_is_rejected() -> None:
    settings = resolve_provider_settings(
        make_config(),
        provider_override="openai",
    )

    with pytest.raises(RuntimeError):
        load_provider_api_key(
            settings,
            environ={},
        )