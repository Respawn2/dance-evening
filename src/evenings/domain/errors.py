"""Domain errors. Carry no HTTP status codes.

Соответствие ошибки коду состояния — знание слоя доставки; живёт в обработчике.
"""


class DomainError(Exception):
    """Base class for rule violations."""


class InvalidEvening(DomainError):
    """The evening is not valid on its own (aggregate invariants)."""


class EveningNotFound(DomainError):
    """No evening with this id."""


class EveningAlreadyStarted(DomainError):
    """The evening has started; registration is closed."""


class InvalidDanceRole(DomainError):
    """The dance role does not match the category of the evening."""


class AlreadyRegistered(DomainError):
    """The user already has an active registration for this evening."""


class EveningFull(DomainError):
    """The evening has no seats left."""
