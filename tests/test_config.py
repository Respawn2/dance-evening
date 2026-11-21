"""Settings parsing and validation."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from evenings.config import Settings

VALID_DATABASE_URL = "postgresql://user:secret@localhost:5432/evenings"


def test_defaults_are_applied(monkeypatch: pytest.MonkeyPatch) -> None:
    # arrange
    monkeypatch.setenv("DATABASE_URL", VALID_DATABASE_URL)

    # act
    settings = Settings()  # type: ignore[call-arg]

    # assert
    assert settings.port == 8080
    assert settings.log_level == "info"
    assert settings.environment == "development"


def test_missing_database_url_is_rejected() -> None:
    with pytest.raises(ValidationError) as error:
        Settings()  # type: ignore[call-arg]

    assert "database_url" in str(error.value)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", 1),
        ("80", 80),
        ("8080", 8080),
        ("65535", 65535),
    ],
    ids=["min", "privileged", "default", "max"],
)
def test_port_is_parsed(monkeypatch: pytest.MonkeyPatch, raw: str, expected: int) -> None:
    monkeypatch.setenv("DATABASE_URL", VALID_DATABASE_URL)
    monkeypatch.setenv("PORT", raw)

    assert Settings().port == expected  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "raw",
    ["0", "-1", "65536", "abc", "", "8080.5"],
    ids=["zero", "negative", "above-max", "letters", "empty", "fractional"],
)
def test_invalid_port_is_rejected(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("DATABASE_URL", VALID_DATABASE_URL)
    monkeypatch.setenv("PORT", raw)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


@pytest.mark.parametrize("raw", ["verbose", "INFO ", "trace", "none"])
def test_unknown_log_level_is_rejected(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("DATABASE_URL", VALID_DATABASE_URL)
    monkeypatch.setenv("LOG_LEVEL", raw)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_unknown_key_in_env_file_is_rejected(tmp_path: Path) -> None:
    """A typo in .env must not pass silently."""
    env_file = tmp_path / ".env"
    env_file.write_text(f"DATABASE_URL={VALID_DATABASE_URL}\nLOG_LEVL=info\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="extra_forbidden"):
        Settings(_env_file=env_file)  # type: ignore[call-arg]


def test_unknown_environment_variable_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """Documents the limit: only declared fields are read from the environment."""
    monkeypatch.setenv("DATABASE_URL", VALID_DATABASE_URL)
    monkeypatch.setenv("LOG_LEVL", "debug")

    assert Settings().log_level == "info"  # type: ignore[call-arg]
