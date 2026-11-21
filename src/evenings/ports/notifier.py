"""Outgoing notifications: the anti-corruption layer of ЛР 2Б.

Метод назван по событию, а не send(text): сервис сообщает факт,
а знание о письмах, адресах и способе доставки живёт в реализации.
Полный перечень событий — в docs/domain/event-storming.md; интерфейс
растёт вместе со сценариями (сейчас нужен только этот метод).
"""

from typing import Protocol

from evenings.domain.models import RegistrationId, UserId


class Notifier(Protocol):
    def registration_created(self, user_id: UserId, registration_id: RegistrationId) -> None: ...
