"""Registration rules, tested one by one, without any I/O."""

from datetime import UTC, datetime, timedelta

import pytest

from evenings.domain.errors import (
    AlreadyRegistered,
    EveningAlreadyStarted,
    EveningFull,
    InvalidDanceRole,
)
from evenings.domain.models import (
    Capacity,
    DanceRole,
    Evening,
    EveningCategory,
    EveningId,
    Registration,
    RegistrationId,
    RegistrationStatus,
    TimeRange,
    UserId,
)
from evenings.domain.rules import (
    RegistrationPolicy,
    require_evening_open,
    require_not_registered_yet,
    require_role_allowed,
    require_seats_available,
)

DANCE_POLICY = RegistrationPolicy(allowed_roles=frozenset({DanceRole.LEADER, DanceRole.FOLLOWER}))
GENERAL_POLICY = RegistrationPolicy(allowed_roles=frozenset({DanceRole.NONE}))


def _evening(capacity: int = 2) -> Evening:
    starts_at = datetime(2030, 11, 15, 20, 0, tzinfo=UTC)
    return Evening(
        id=EveningId("evening-1"),
        category=EveningCategory.DANCE,
        title="Бачата в баре «Ленинград»",
        interval=TimeRange(starts_at, starts_at + timedelta(hours=3)),
        capacity=Capacity(capacity),
    )


@pytest.mark.parametrize(
    "role",
    [DanceRole.LEADER, DanceRole.FOLLOWER],
    ids=["leader", "follower"],
)
def test_dance_policy_allows_pair_roles(role: DanceRole) -> None:
    require_role_allowed(DANCE_POLICY, role)  # does not raise


def test_dance_policy_rejects_missing_role() -> None:
    with pytest.raises(InvalidDanceRole):
        require_role_allowed(DANCE_POLICY, DanceRole.NONE)


def test_general_policy_rejects_pair_role() -> None:
    with pytest.raises(InvalidDanceRole):
        require_role_allowed(GENERAL_POLICY, DanceRole.LEADER)


def test_general_policy_allows_no_role() -> None:
    require_role_allowed(GENERAL_POLICY, DanceRole.NONE)  # does not raise


def test_evening_is_open_a_minute_before_start() -> None:
    evening = _evening()
    now = evening.interval.starts_at - timedelta(minutes=1)

    require_evening_open(evening, now)  # does not raise


def test_evening_is_closed_from_the_start_moment() -> None:
    """Полуоткрытый интервал: в момент начала запись уже закрыта (AC-05.2)."""
    evening = _evening()

    with pytest.raises(EveningAlreadyStarted):
        require_evening_open(evening, evening.interval.starts_at)


def test_seats_available_below_capacity() -> None:
    require_seats_available(_evening(capacity=2), active_count=1)  # does not raise


def test_no_seats_at_capacity() -> None:
    with pytest.raises(EveningFull):
        require_seats_available(_evening(capacity=2), active_count=2)


def test_no_active_registration_allows_one() -> None:
    require_not_registered_yet(None)  # does not raise


def test_active_registration_blocks_duplicate() -> None:
    existing = Registration(
        id=RegistrationId("r-1"),
        evening_id=EveningId("evening-1"),
        user_id=UserId("u-1"),
        dance_role=DanceRole.FOLLOWER,
        status=RegistrationStatus.ACTIVE,
        created_at=datetime(2030, 11, 15, 12, 0, tzinfo=UTC),
    )

    with pytest.raises(AlreadyRegistered):
        require_not_registered_yet(existing)
