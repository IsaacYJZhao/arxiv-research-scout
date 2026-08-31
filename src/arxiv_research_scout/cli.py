from __future__ import annotations

import argparse
import os
from collections.abc import (
    Mapping,
    Sequence,
)
from dataclasses import dataclass

from arxiv_research_scout.config import (
    load_config,
)
from arxiv_research_scout.llm_provider import (
    VALID_PROVIDERS,
    resolve_provider_settings,
)
from arxiv_research_scout.models import (
    LLMProviderSettings,
)
from arxiv_research_scout.paths import (
    resolve_project_path,
)
from arxiv_research_scout.runner import (
    print_scan_result,
    run_scan,
)
from arxiv_research_scout.state_manager import (
    load_state,
)


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    """
    Safe runtime information about one LLM provider.

    The actual API key is never stored here.
    """

    settings: LLMProviderSettings
    api_key_configured: bool


def resolve_provider_status(
    config: dict,
    *,
    provider_override: str | None = None,
    model_override: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> ProviderStatus:
    """
    Resolve provider/model selection without making
    any API request.

    Only the presence of the API key is checked.
    The key itself is never returned or printed.
    """

    settings = resolve_provider_settings(
        config,
        provider_override=provider_override,
        model_override=model_override,
    )

    environment = (
        os.environ
        if environ is None
        else environ
    )

    api_key_configured = bool(
        environment.get(
            settings.api_key_env,
            "",
        ).strip()
    )

    return ProviderStatus(
        settings=settings,
        api_key_configured=api_key_configured,
    )


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line interface.
    """

    parser = argparse.ArgumentParser(
        prog="arxiv-scout",
        description=(
            "Monitor arXiv research topics and "
            "generate structured literature digests."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # --------------------------------------------------
    # scan
    # --------------------------------------------------

    scan_parser = subparsers.add_parser(
        "scan",
        help=(
            "Search arXiv and show papers selected "
            "by the retrieval pipeline."
        ),
    )

    scan_parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Ignore the configured scheduling "
            "interval for this scan."
        ),
    )

    # --------------------------------------------------
    # provider
    # --------------------------------------------------

    provider_parser = subparsers.add_parser(
        "provider",
        help=(
            "Inspect the LLM provider/model that "
            "would be used at runtime."
        ),
    )

    provider_parser.add_argument(
        "--provider",
        choices=sorted(
            VALID_PROVIDERS
        ),
        default=None,
        help=(
            "Temporarily override the default "
            "provider."
        ),
    )

    provider_parser.add_argument(
        "--model",
        default=None,
        help=(
            "Temporarily override the model "
            "configured for the selected provider."
        ),
    )

    return parser


def run_scan_command(
    *,
    force: bool,
) -> int:
    """
    Execute the existing arXiv scan pipeline.
    """

    config = load_config()

    state_file = resolve_project_path(
        config["state"]["file"]
    )

    state = load_state(
        state_file
    )

    result = run_scan(
        config=config,
        state=state,
        force=force,
    )

    print_scan_result(
        config,
        result,
    )

    return 0


def run_provider_command(
    *,
    provider_override: str | None,
    model_override: str | None,
) -> int:
    """
    Display provider information safely.

    No network/API request is made.
    """

    config = load_config()

    status = resolve_provider_status(
        config,
        provider_override=provider_override,
        model_override=model_override,
    )

    settings = status.settings

    print()
    print(
        "===== LLM Provider ====="
    )
    print()

    print(
        f"Provider           : "
        f"{settings.provider}"
    )

    print(
        f"Model              : "
        f"{settings.model}"
    )

    print(
        f"API key variable   : "
        f"{settings.api_key_env}"
    )

    print(
        f"API key configured : "
        f"{'yes' if status.api_key_configured else 'no'}"
    )

    if settings.base_url:
        print(
            f"Base URL           : "
            f"{settings.base_url}"
        )
    else:
        print(
            "Base URL           : "
            "OpenAI SDK default"
        )

    print(
        f"Max output tokens  : "
        f"{settings.max_output_tokens}"
    )

    print()

    return 0


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Main command-line entry point.
    """

    parser = build_parser()

    args = parser.parse_args(
        argv
    )

    if args.command == "scan":
        return run_scan_command(
            force=args.force,
        )

    if args.command == "provider":
        return run_provider_command(
            provider_override=(
                args.provider
            ),
            model_override=(
                args.model
            ),
        )

    parser.error(
        f"Unknown command: "
        f"{args.command}"
    )

    return 2


if __name__ == "__main__":
    raise SystemExit(
        main()
    )