"""Registrations in memory. Used until ЛР 4 introduces PostgreSQL."""

from evenings.domain.models import (
    EveningId,
    Registration,
    RegistrationStatus,
    UserId,
)


class InMemoryRegistrationRepository:
    """Storage in memory. A fresh instance per test gives a known initial state."""

    def __init__(self) -> None:
        self._registrations: list[Registration] = []

    def add(self, registration: Registration) -> None:
        self._registrations.append(registration)

    def find_active(self, evening_id: EveningId, user_id: UserId) -> Registration | None:
        return next(
            (
                registration
                for registration in self._registrations
                if registration.evening_id == evening_id
                and registration.user_id == user_id
                and registration.status is RegistrationStatus.ACTIVE
            ),
            None,
        )

    def count_active(self, evening_id: EveningId) -> int:
        return sum(
            1
            for registration in self._registrations
            if registration.evening_id == evening_id
            and registration.status is RegistrationStatus.ACTIVE
        )
