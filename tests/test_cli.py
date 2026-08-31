import pytest
from pathlib import Path

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

def test_cli_parser_accepts_full_run() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "run",
            "--force",
            "--provider",
            "deepseek",
            "--model",
            "temporary-model",
        ]
    )

    assert args.command == "run"
    assert args.force

    assert args.provider == (
        "deepseek"
    )

    assert args.model == (
        "temporary-model"
    )

def test_cli_parser_accepts_analyze_paper() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "analyze-paper",
            "2608.16855v1",
            "--provider",
            "deepseek",
        ]
    )

    assert args.command == (
        "analyze-paper"
    )

    assert args.arxiv_id == (
        "2608.16855v1"
    )

    assert args.provider == (
        "deepseek"
    )

def test_run_parser_supports_digest_workflow() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "run",
            "--force",
            "--provider",
            "deepseek",
            "--model",
            "temporary-model",
        ]
    )

    assert args.command == "run"
    assert args.force

    assert (
        args.provider
        == "deepseek"
    )

    assert (
        args.model
        == "temporary-model"
    )


def test_run_workflow_command_returns_workflow_exit_code(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from arxiv_research_scout import cli

    fake_result = object()
    captured = {}

    monkeypatch.setattr(
        cli,
        "load_config",
        lambda: {
            "state": {
                "file": ".state/state.json",
            },
            "output": {
                "reports_dir": "reports",
            },
        },
    )

    monkeypatch.setattr(
        cli,
        "resolve_project_path",
        lambda path: (
            tmp_path / "state.json"
        ),
    )

    monkeypatch.setattr(
        cli,
        "resolve_reports_dir",
        lambda config: (
            tmp_path / "reports"
        ),
    )

    monkeypatch.setattr(
        cli,
        "load_state",
        lambda path: {
            "schema_version": 1,
            "last_successful_run_utc": None,
            "processed_ids": [],
        },
    )

    def fake_workflow(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return fake_result

    monkeypatch.setattr(
        cli,
        "run_research_workflow",
        fake_workflow,
    )

    monkeypatch.setattr(
        cli,
        "print_workflow_result",
        lambda config, result: None,
    )

    monkeypatch.setattr(
        cli,
        "workflow_exit_code",
        lambda result: 1,
    )

    exit_code = (
        cli.run_workflow_command(
            force=True,
            provider_override="deepseek",
            model_override="temporary-model",
        )
    )

    assert exit_code == 1

    assert (
        captured["force"]
        is True
    )

    assert (
        captured["provider_override"]
        == "deepseek"
    )

    assert (
        captured["model_override"]
        == "temporary-model"
    )


def test_run_workflow_command_prints_workflow_result(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from arxiv_research_scout import cli

    fake_result = object()
    print_called = False

    monkeypatch.setattr(
        cli,
        "load_config",
        lambda: {
            "state": {
                "file": ".state/state.json",
            },
            "output": {
                "reports_dir": "reports",
            },
        },
    )

    monkeypatch.setattr(
        cli,
        "resolve_project_path",
        lambda path: (
            tmp_path / "state.json"
        ),
    )

    monkeypatch.setattr(
        cli,
        "resolve_reports_dir",
        lambda config: (
            tmp_path / "reports"
        ),
    )

    monkeypatch.setattr(
        cli,
        "load_state",
        lambda path: {},
    )

    monkeypatch.setattr(
        cli,
        "run_research_workflow",
        lambda **kwargs: (
            fake_result
        ),
    )

    def fake_print(
        config,
        result,
    ):
        nonlocal print_called

        print_called = True

        assert (
            result
            is fake_result
        )

    monkeypatch.setattr(
        cli,
        "print_workflow_result",
        fake_print,
    )

    monkeypatch.setattr(
        cli,
        "workflow_exit_code",
        lambda result: 0,
    )

    exit_code = (
        cli.run_workflow_command(
            force=False,
            provider_override=None,
            model_override=None,
        )
    )

    assert exit_code == 0
    assert print_called


def test_run_workflow_command_propagates_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from arxiv_research_scout import cli

    monkeypatch.setattr(
        cli,
        "load_config",
        lambda: {
            "state": {
                "file": ".state/state.json",
            },
            "output": {
                "reports_dir": "reports",
            },
        },
    )

    monkeypatch.setattr(
        cli,
        "resolve_project_path",
        lambda path: (
            tmp_path / "state.json"
        ),
    )

    monkeypatch.setattr(
        cli,
        "resolve_reports_dir",
        lambda config: (
            tmp_path / "reports"
        ),
    )

    monkeypatch.setattr(
        cli,
        "load_state",
        lambda path: {},
    )

    def failing_workflow(
        **kwargs,
    ):
        raise RuntimeError(
            "digest failed"
        )

    monkeypatch.setattr(
        cli,
        "run_research_workflow",
        failing_workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="digest failed",
    ):
        cli.run_workflow_command(
            force=True,
            provider_override="deepseek",
            model_override=None,
        )