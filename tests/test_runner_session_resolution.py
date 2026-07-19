from pathlib import Path

from runner import resolve_telegram_session_config


def test_resolve_telegram_session_config_prefers_environment_value() -> None:
    session_string, session_name = resolve_telegram_session_config("abc123")

    assert session_string == "abc123"
    assert session_name == "environment"


def test_resolve_telegram_session_config_falls_back_to_repo_session_file(tmp_path: Path) -> None:
    session_file = tmp_path / "subforge.session"
    session_file.write_text("fake-session", encoding="utf-8")

    session_string, session_name = resolve_telegram_session_config(None, session_file)

    assert session_string is None
    assert session_name == "subforge"
