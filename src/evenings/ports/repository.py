"""What the service needs from storage. Declared by the consumer.

Агрегаты «Вечер» и «Запись» разделены (ЛР 2Б), поэтому порта два;
в каждом — только методы, нужные текущему сценарию (разделение интерфейсов).
"""

from typing import Protocol

from evenings.domain.models import Evening, EveningId, Registration, UserId


class EveningRepository(Protocol):
    def get(self, evening_id: EveningId) -> Evening | None: ...


class RegistrationRepository(Protocol):
    def add(self, registration: Registration) -> None: ...

    def find_active(self, evening_id: EveningId, user_id: UserId) -> Registration | None: ...

    def count_active(self, evening_id: EveningId) -> int: ...
