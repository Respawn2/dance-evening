"""Composition root: the single place where implementations are chosen.

It belongs to the delivery layer: it wires FastAPI dependencies,
and domain/ and services/ must not know about the framework (ADR-0003).
"""

from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from evenings.adapters.in_memory_evening_repository import InMemoryEveningRepository
from evenings.adapters.in_memory_registration_repository import (
    InMemoryRegistrationRepository,
)
from evenings.adapters.logging_notifier import LoggingNotifier
from evenings.adapters.system_clock import SystemClock, UuidIdGenerator
from evenings.config import Settings, get_settings
from evenings.domain.models import Capacity, Evening, EveningCategory, EveningId, TimeRange
from evenings.services.policies import policy_for
from evenings.services.registration_service import RegistrationService


@lru_cache
def _evenings() -> InMemoryEveningRepository:
    """Single instance: in-memory storage must survive between requests.

    Seeded with demo evenings until the publishing scenario and PostgreSQL
    arrive in ЛР 4; the seeding disappears together with this adapter.
    """
    return InMemoryEveningRepository(_demo_evenings())


@lru_cache
def _registrations() -> InMemoryRegistrationRepository:
    """Single instance: in-memory storage must survive between requests."""
    return InMemoryRegistrationRepository()


def get_registration_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationService:
    """Build the scenario with the implementations chosen for this process."""
    return RegistrationService(
        evenings=_evenings(),
        registrations=_registrations(),
        clock=SystemClock(),
        ids=UuidIdGenerator(),
        notifier=LoggingNotifier(),
        policy_for=policy_for,
    )


def _demo_evenings() -> list[Evening]:
    """Демо-вечера для запуска и тестов доставки; те же, что до рефакторинга."""
    return [
        Evening(
            id=EveningId("evening-1"),
            category=EveningCategory.DANCE,
            title="Бачата в баре «Ленинград»",
            interval=TimeRange(
                _moment("2030-11-15T20:00:00+00:00"), _moment("2030-11-15T23:00:00+00:00")
            ),
            capacity=Capacity(40),
        ),
        Evening(
            id=EveningId("evening-2"),
            category=EveningCategory.QUIZ,
            title="Квиз-вечер: музыка 90-х",
            interval=TimeRange(
                _moment("2030-11-18T19:00:00+00:00"), _moment("2030-11-18T22:00:00+00:00")
            ),
            capacity=Capacity(10),
        ),
        Evening(
            id=EveningId("evening-3"),
            category=EveningCategory.DANCE,
            title="Сальса: открытый урок",
            interval=TimeRange(
                _moment("2020-01-01T20:00:00+00:00"), _moment("2020-01-01T23:00:00+00:00")
            ),
            capacity=Capacity(10),
        ),
        Evening(
            id=EveningId("evening-4"),
            category=EveningCategory.DANCE,
            title="Меренге-вечеринка",
            interval=TimeRange(
                _moment("2030-11-20T20:00:00+00:00"), _moment("2030-11-20T23:00:00+00:00")
            ),
            capacity=Capacity(1),
        ),
    ]


def _moment(raw: str) -> datetime:
    return datetime.fromisoformat(raw)
