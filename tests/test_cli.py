from arxiv_research_scout.cli import (
    build_parser,
    resolve_provider_status,
)


def make_config() -> dict:
    return {
        "llm": {
            "default_provider": (
                "openai"
            ),
            "max_output_tokens": 2500,
            "openai": {
                "model": (
                    "gpt-5.6-terra"
                ),
            },
            "deepseek": {
                "model": (
                    "deepseek-v4-pro"
                ),
                "base_url": (
                    "https://api.deepseek.com"
                ),
            },
        }
    }


def test_provider_status_uses_default() -> None:
    status = resolve_provider_status(
        make_config(),
        environ={},
    )

    assert (
        status.settings.provider
        == "openai"
    )

    assert (
        status.settings.model
        == "gpt-5.6-terra"
    )


def test_provider_status_uses_override() -> None:
    status = resolve_provider_status(
        make_config(),
        provider_override="deepseek",
        environ={},
    )

    assert (
        status.settings.provider
        == "deepseek"
    )

    assert (
        status.settings.model
        == "deepseek-v4-pro"
    )


def test_provider_status_detects_api_key() -> None:
    status = resolve_provider_status(
        make_config(),
        provider_override="deepseek",
        environ={
            "DEEPSEEK_API_KEY": (
                "test-secret"
            )
        },
    )

    assert status.api_key_configured


def test_provider_status_handles_missing_key() -> None:
    status = resolve_provider_status(
        make_config(),
        provider_override="openai",
        environ={},
    )

    assert not (
        status.api_key_configured
    )


def test_cli_parser_accepts_scan_force() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "scan",
            "--force",
        ]
    )

    assert args.command == "scan"
    assert args.force


def test_cli_parser_accepts_provider_and_model() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "provider",
            "--provider",
            "deepseek",
            "--model",
            "deepseek-v4-flash",
        ]
    )

    assert args.command == "provider"

    assert args.provider == (
        "deepseek"
    )

    assert args.model == (
        "deepseek-v4-flash"
    )