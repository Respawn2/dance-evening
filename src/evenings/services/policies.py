"""Допустимые роли в паре по категориям вечера: таблица стратегии.

Третья категория со своими правилами — новый член EveningCategory,
новая политика и строка в таблице; RegistrationService и правила не меняются.
"""

from evenings.domain.models import DanceRole, EveningCategory
from evenings.domain.rules import RegistrationPolicy

DANCE_REGISTRATION_POLICY = RegistrationPolicy(
    allowed_roles=frozenset({DanceRole.LEADER, DanceRole.FOLLOWER}),
)
GENERAL_REGISTRATION_POLICY = RegistrationPolicy(
    allowed_roles=frozenset({DanceRole.NONE}),
)

_POLICY_BY_CATEGORY: dict[EveningCategory, RegistrationPolicy] = {
    EveningCategory.DANCE: DANCE_REGISTRATION_POLICY,
    EveningCategory.STANDUP: GENERAL_REGISTRATION_POLICY,
    EveningCategory.QUIZ: GENERAL_REGISTRATION_POLICY,
    EveningCategory.CONCERT: GENERAL_REGISTRATION_POLICY,
    EveningCategory.GAMES: GENERAL_REGISTRATION_POLICY,
}


def policy_for(category: EveningCategory) -> RegistrationPolicy:
    return _POLICY_BY_CATEGORY[category]
