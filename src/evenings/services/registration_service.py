"""The create-registration scenario (FR-04)."""

from collections.abc import Callable

import structlog

from evenings.domain import rules
from evenings.domain.errors import EveningNotFound
from evenings.domain.models import (
    EveningCategory,
    Registration,
    RegistrationRequest,
    RegistrationStatus,
)
from evenings.domain.rules import RegistrationPolicy
from evenings.ports.clock import Clock, IdGenerator
from evenings.ports.notifier import Notifier
from evenings.ports.repository import EveningRepository, RegistrationRepository

PolicyFor = Callable[[EveningCategory], RegistrationPolicy]


class RegistrationService:
    """Создаёт записи на вечера. Не знает ничего о HTTP и SQL."""

    def __init__(
        self,
        evenings: EveningRepository,
        registrations: RegistrationRepository,
        clock: Clock,
        ids: IdGenerator,
        notifier: Notifier,
        policy_for: PolicyFor,
    ) -> None:
        self._evenings = evenings
        self._registrations = registrations
        self._clock = clock
        self._ids = ids
        self._notifier = notifier
        self._policy_for = policy_for

    def create(self, request: RegistrationRequest) -> Registration:
        evening = self._evenings.get(request.evening_id)
        if evening is None:
            raise EveningNotFound(f"evening {request.evening_id} not found")

        policy = self._policy_for(evening.category)
        now = self._clock.now()

        rules.require_evening_open(evening, now)
        rules.require_role_allowed(policy, request.dance_role)
        rules.require_not_registered_yet(
            self._registrations.find_active(request.evening_id, request.user_id)
        )
        rules.require_seats_available(evening, self._registrations.count_active(evening.id))

        registration = Registration(
            id=self._ids.next_id(),
            evening_id=request.evening_id,
            user_id=request.user_id,
            dance_role=request.dance_role,
            status=RegistrationStatus.ACTIVE,
            created_at=now,
        )
        self._registrations.add(registration)
        self._notify(registration)

        structlog.get_logger().info(
            "registration_created",
            registration_id=registration.id,
            evening_id=registration.evening_id,
        )
        return registration

    def _notify(self, registration: Registration) -> None:
        """AC-10.2: отказ доставки не отказывает запись — уведомление не часть агрегата."""
        try:
            self._notifier.registration_created(registration.user_id, registration.id)
        except Exception:
            structlog.get_logger().warning(
                "registration_notification_failed",
                registration_id=registration.id,
            )
