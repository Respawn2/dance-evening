"""Adapter over a PostgreSQL connection. Implemented in ЛР 4А.

Declared now so that the shape of the boundary is fixed: the service
depends on RegistrationRepository and will not change when storage does.
"""

from evenings.domain.models import EveningId, Registration, UserId


class PostgresRegistrationRepository:
    def __init__(self, connection: object) -> None:
        self._connection = connection

    def add(self, registration: Registration) -> None:
        raise NotImplementedError("ЛР 4А")

    def find_active(self, evening_id: EveningId, user_id: UserId) -> Registration | None:
        raise NotImplementedError("ЛР 4А")

    def count_active(self, evening_id: EveningId) -> int:
        raise NotImplementedError("ЛР 4А")
