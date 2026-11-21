"""Domain objects. No knowledge of HTTP, SQL or frameworks.

Имена классов и значений — из глоссария ЛР 2Б (domain/ubiquitous-language.md),
инварианты — из описания агрегатов (domain/aggregates.md).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import NewType

from evenings.domain.errors import InvalidEvening

EveningId = NewType("EveningId", str)
RegistrationId = NewType("RegistrationId", str)
UserId = NewType("UserId", str)
Capacity = NewType("Capacity", int)


class EveningCategory(StrEnum):
    """Категория вечера: определяет, нужны ли роли в паре и выравнивание цены."""

    DANCE = "dance"
    STANDUP = "standup"
    QUIZ = "quiz"
    CONCERT = "concert"
    GAMES = "games"


class DanceRole(StrEnum):
    """Роль в паре: ведущий или ведомая. Существует только у танцевальных вечеров.

    NONE — внутреннее представление отсутствия роли у остальных категорий;
    наружу оно показывается как null.
    """

    LEADER = "leader"
    FOLLOWER = "follower"
    NONE = "none"


class RegistrationStatus(StrEnum):
    """Статусы записи; «вечер отменён» — не статус записи, а состояние вечера."""

    ACTIVE = "active"
    CONFIRMED = "confirmed"  # RSVP, появится в ЛР 6А
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"
    ARRIVED = "arrived"
    NO_SHOW = "no_show"


class EveningStatus(StrEnum):
    """Хранятся announced и cancelled; ongoing и finished вычисляются по времени."""

    ANNOUNCED = "announced"
    CANCELLED = "cancelled"


# И-2 из ЛР 2Б: длительность вечера — от 30 минут до 12 часов.
MIN_EVENING_DURATION = timedelta(minutes=30)
MAX_EVENING_DURATION = timedelta(hours=12)


@dataclass(frozen=True, slots=True)
class TimeRange:
    """Полуоткрытый интервал вечера [starts_at, ends_at) — инвариант И-1."""

    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        """Инвариант значения: пустой или перевёрнутый интервал не может существовать."""
        if self.ends_at <= self.starts_at:
            raise InvalidEvening("end must be after start")

    @property
    def duration(self) -> timedelta:
        return self.ends_at - self.starts_at


@dataclass(frozen=True, slots=True)
class Evening:
    """Агрегат «Вечер» — корень границы согласованности (ЛР 2Б)."""

    id: EveningId
    category: EveningCategory
    title: str
    interval: TimeRange
    capacity: Capacity
    status: EveningStatus = EveningStatus.ANNOUNCED

    def __post_init__(self) -> None:
        """Инварианты агрегата: И-2, И-3, И-7 из ЛР 2Б."""
        if not self.title:
            raise InvalidEvening("title must not be empty")
        if self.capacity < 1:
            raise InvalidEvening("capacity must be positive")
        if not MIN_EVENING_DURATION <= self.interval.duration <= MAX_EVENING_DURATION:
            raise InvalidEvening("evening duration must be between 30 minutes and 12 hours")

    def started(self, now: datetime) -> bool:
        """Информационный эксперт: вечер сам знает, начался ли он.

        Полуоткрытый интервал: в момент начала вечер уже начался (AC-05.2).
        """
        return self.interval.starts_at <= now


@dataclass(frozen=True, slots=True)
class RegistrationRequest:
    """Что нужно для создания записи."""

    evening_id: EveningId
    user_id: UserId
    dance_role: DanceRole


@dataclass(frozen=True, slots=True)
class Registration:
    """Агрегат «Запись» — корень границы согласованности (ЛР 2Б).

    Инвариант И-8 (роль обязательна для танцевальной категории) проверяется
    правилом require_role_allowed до создания: категория приходит с политикой.
    """

    id: RegistrationId
    evening_id: EveningId
    user_id: UserId
    dance_role: DanceRole
    status: RegistrationStatus
    created_at: datetime
