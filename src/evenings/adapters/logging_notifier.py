"""Writes a structured event. Replaced by a real channel in ЛР 6А."""

import structlog

from evenings.domain.models import RegistrationId, UserId


class LoggingNotifier:
    """Честная заглушка на период, когда настоящего канала оповещений нет."""

    def registration_created(self, user_id: UserId, registration_id: RegistrationId) -> None:
        structlog.get_logger().info(
            "registration_created_notified",
            user_id=user_id,
            registration_id=registration_id,
        )
