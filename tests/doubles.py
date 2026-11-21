"""Hand-written test doubles. Conformance to the protocols is checked by mypy."""

from datetime import datetime

from evenings.domain.models import RegistrationId, UserId


class FixedClock:
    """Stub: returns the moment given to it."""

    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment


class SequentialIds:
    """Stub: predictable identifiers r-1, r-2, …"""

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> RegistrationId:
        self._counter += 1
        return RegistrationId(f"r-{self._counter}")


class SpyNotifier:
    """Spy: records calls so that the test can assert on them."""

    def __init__(self) -> None:
        self.notified: list[tuple[UserId, RegistrationId]] = []

    def registration_created(self, user_id: UserId, registration_id: RegistrationId) -> None:
        self.notified.append((user_id, registration_id))


class FailingNotifier:
    """Stub for the failure path: the channel is unavailable (AC-10.2)."""

    def registration_created(self, user_id: UserId, registration_id: RegistrationId) -> None:
        raise RuntimeError("notification channel is down")
