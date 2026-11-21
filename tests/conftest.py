"""Shared fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evenings.api import dependencies
from evenings.app import create_app
from evenings.config import Settings

TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test"


@pytest.fixture(autouse=True)
def _fresh_storage() -> None:
    """Каждый тест — с чистым хранилищем: кеш корня композиции сбрасывается.

    Стало возможным после рефакторинга: состояние хранилища больше не
    глобальная переменная модуля, и исходное состояние задаётся фикстурой.
    """
    dependencies._evenings.cache_clear()
    dependencies._registrations.cache_clear()


@pytest.fixture
def settings() -> Settings:
    """Settings for tests: explicit, not read from the developer machine.

    A setting that becomes required in a later work is added here
    and to .env.example in the same commit.
    """
    return Settings(
        environment="test",
        log_level="warning",
        app_version="0.0.0-test",
        database_url=TEST_DATABASE_URL,  # type: ignore[arg-type]
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    """Test client calling the application in-process."""
    with TestClient(create_app(settings=settings)) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep tests away from the machine: no application variables, no .env.

    Settings read .env from the working directory, so every test runs
    in an empty temporary directory.
    """
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    monkeypatch.chdir(tmp_path)
