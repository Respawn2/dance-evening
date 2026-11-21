"""Registration rules. Pure functions of their arguments.

Каждая функция — правило сценария из ЛР 2Б (раздел «Что инвариантом не
является»); инварианты агрегатов живут в самих агрегатах (models.py).
"""

from dataclasses import dataclass
from datetime import datetime

from evenings.domain.errors import (
    AlreadyRegistered,
    EveningAlreadyStarted,
    EveningFull,
    InvalidDanceRole,
)
from evenings.domain.models import DanceRole, Evening, Registration


@dataclass(frozen=True, slots=True)
class RegistrationPolicy:
    """Правила записи, зависящие от категории вечера (стратегия).

    Категории различаются только допустимыми ролями в паре, поэтому политика —
    объект-значение с данными, а не иерархия классов с методом check().
    """

    allowed_roles: frozenset[DanceRole]


def require_role_allowed(policy: RegistrationPolicy, role: DanceRole) -> None:
    """И-8 из ЛР 2Б: у танцевальных вечеров роль в паре обязательна, у остальных запрещена."""
    if role not in policy.allowed_roles:
        raise InvalidDanceRole(f"role {role} is not allowed for this evening category")


def require_evening_open(evening: Evening, now: datetime) -> None:
    """AC-04.6: запись закрыта с момента начала вечера. `now` — аргумент, не системные часы."""
    if evening.started(now):
        raise EveningAlreadyStarted(f"evening {evening.id} has already started")


def require_not_registered_yet(existing: Registration | None) -> None:
    """AC-04.4: повторная действующая запись того же пользователя отвергается."""
    if existing is not None:
        raise AlreadyRegistered("user already has an active registration for this evening")


def require_seats_available(evening: Evening, active_count: int) -> None:
    """AC-04.2 и AC-04.3: лимит мест.

    Правило сценария, а не инвариант агрегата: нужны другие записи.
    От состязания двух запросов за последнее место защищает база (ЛР 4А).
    """
    if active_count >= evening.capacity:
        raise EveningFull(f"evening {evening.id} has no seats left")
