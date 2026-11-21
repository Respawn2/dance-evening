"""The scenario, tested without a server and without a database."""

from datetime import UTC, datetime, timedelta

import pytest

from evenings.adapters.in_memory_evening_repository import InMemoryEveningRepository
from evenings.adapters.in_memory_registration_repository import (
    InMemoryRegistrationRepository,
)
from evenings.domain.errors import (
    AlreadyRegistered,
    EveningAlreadyStarted,
    EveningFull,
    EveningNotFound,
    InvalidDanceRole,
)
from evenings.domain.models import (
    Capacity,
    DanceRole,
    Evening,
    EveningCategory,
    EveningId,
    RegistrationRequest,
    TimeRange,
    UserId,
)
from evenings.services.policies import policy_for
from evenings.services.registration_service import RegistrationService
from tests.doubles import FailingNotifier, FixedClock, SequentialIds, SpyNotifier

NOW = datetime(2030, 11, 15, 12, 0, tzinfo=UTC)


def _evening(
    evening_id: str = "evening-1",
    category: EveningCategory = EveningCategory.DANCE,
    capacity: int = 40,
    starts_at: datetime | None = None,
) -> Evening:
    starts = starts_at or datetime(2030, 11, 15, 20, 0, tzinfo=UTC)
    return Evening(
        id=EveningId(evening_id),
        category=category,
        title="Бачата в баре «Ленинград»",
        interval=TimeRange(starts, starts + timedelta(hours=3)),
        capacity=Capacity(capacity),
    )


def _request(
    evening_id: str = "evening-1",
    user: str = "u-1",
    role: DanceRole = DanceRole.FOLLOWER,
) -> RegistrationRequest:
    return RegistrationRequest(
        evening_id=EveningId(evening_id),
        user_id=UserId(user),
        dance_role=role,
    )


def _service(
    *evenings: Evening,
    clock: FixedClock | None = None,
    notifier: SpyNotifier | FailingNotifier | None = None,
) -> tuple[RegistrationService, SpyNotifier | FailingNotifier]:
    spy = notifier if notifier is not None else SpyNotifier()
    return (
        RegistrationService(
            evenings=InMemoryEveningRepository(seed=evenings),
            registrations=InMemoryRegistrationRepository(),
            clock=clock or FixedClock(NOW),
            ids=SequentialIds(),
            notifier=spy,
            policy_for=policy_for,
        ),
        spy,
    )


def test_registration_gets_a_generated_id() -> None:
    service, _ = _service(_evening())

    registration = service.create(_request())

    assert registration.id == "r-1"


def test_duplicate_registration_is_rejected() -> None:
    service, _ = _service(_evening())
    service.create(_request(user="u-1"))

    with pytest.raises(AlreadyRegistered):
        service.create(_request(user="u-1"))


def test_last_seat_is_taken_exactly_once() -> None:
    """AC-04.3: при лимите 2 двое записываются, третий получает отказ."""
    service, _ = _service(_evening(capacity=2))
    service.create(_request(user="u-1"))
    service.create(_request(user="u-2", role=DanceRole.LEADER))

    with pytest.raises(EveningFull):
        service.create(_request(user="u-3"))


def test_dance_evening_rejects_missing_role() -> None:
    """AC-04.5: на танцевальный вечер нужна роль в паре."""
    service, _ = _service(_evening())

    with pytest.raises(InvalidDanceRole):
        service.create(_request(role=DanceRole.NONE))


def test_quiz_evening_rejects_a_role() -> None:
    """AC-04.5: у квиза ролей в паре нет, передача роли отвергается."""
    service, _ = _service(_evening(category=EveningCategory.QUIZ))

    with pytest.raises(InvalidDanceRole):
        service.create(_request(role=DanceRole.LEADER))


def test_evening_is_open_a_minute_before_start() -> None:
    """Граница AC-04.6: за минуту до начала запись ещё открыта."""
    starts_at = datetime(2030, 11, 15, 20, 0, tzinfo=UTC)
    service, _ = _service(
        _evening(starts_at=starts_at),
        clock=FixedClock(starts_at - timedelta(minutes=1)),
    )

    assert service.create(_request()).id == "r-1"


def test_evening_is_closed_from_the_start_moment() -> None:
    """Граница AC-05.2: в момент начала запись закрыта — полуоткрытый интервал."""
    starts_at = datetime(2030, 11, 15, 20, 0, tzinfo=UTC)
    service, _ = _service(
        _evening(starts_at=starts_at),
        clock=FixedClock(starts_at),
    )

    with pytest.raises(EveningAlreadyStarted):
        service.create(_request())


def test_user_is_notified() -> None:
    """Spy in use: the outgoing action is the requirement itself (FR-10)."""
    service, notifier = _service(_evening())

    registration = service.create(_request())

    assert notifier.notified == [(registration.user_id, registration.id)]


def test_rejected_registration_does_not_notify() -> None:
    service, notifier = _service(_evening(capacity=1))
    service.create(_request(user="u-1"))

    with pytest.raises(EveningFull):
        service.create(_request(user="u-2"))

    assert len(notifier.notified) == 1


def test_notification_failure_does_not_break_registration() -> None:
    """AC-10.2: отказ доставки фиксируется, запись остаётся действующей."""
    service, failing = _service(_evening(), notifier=FailingNotifier())

    registration = service.create(_request())

    assert registration.status == "active"
    assert isinstance(failing, FailingNotifier)


def test_unknown_evening_is_rejected() -> None:
    service, _ = _service(_evening())

    with pytest.raises(EveningNotFound):
        service.create(_request(evening_id="nope"))


@pytest.mark.parametrize(
    ("category", "role", "rejected"),
    [
        (EveningCategory.DANCE, DanceRole.LEADER, False),
        (EveningCategory.DANCE, DanceRole.NONE, True),
        (EveningCategory.QUIZ, DanceRole.NONE, False),
        (EveningCategory.QUIZ, DanceRole.LEADER, True),
    ],
    ids=["dance-leader", "dance-without-role", "quiz-without-role", "quiz-with-role"],
)
def test_strategy_picks_roles_by_category(
    category: EveningCategory, role: DanceRole, rejected: bool
) -> None:
    """Strategy in use: the same request, the category decides the outcome."""
    service, _ = _service(_evening(category=category))
    request = _request(role=role)

    if rejected:
        with pytest.raises(InvalidDanceRole):
            service.create(request)
    else:
        assert service.create(request).id == "r-1"
