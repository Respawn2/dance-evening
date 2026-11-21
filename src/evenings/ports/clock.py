"""Clock and identifier generation: seams for time and randomness."""

from datetime import datetime
from typing import Protocol

from evenings.domain.models import RegistrationId


class Clock(Protocol):
    def now(self) -> datetime: ...


class IdGenerator(Protocol):
    def next_id(self) -> RegistrationId: ...
