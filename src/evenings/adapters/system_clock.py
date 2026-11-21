"""System clock and UUID identifiers: real implementations of the seams."""

from datetime import UTC, datetime
from uuid import uuid4

from evenings.domain.models import RegistrationId


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class UuidIdGenerator:
    def next_id(self) -> RegistrationId:
        return RegistrationId(str(uuid4()))
