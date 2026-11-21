"""Evenings in memory. Used until ЛР 4 introduces PostgreSQL."""

from collections.abc import Iterable

from evenings.domain.models import Evening, EveningId


class InMemoryEveningRepository:
    """Storage in memory. Seeded through the constructor, not baked in."""

    def __init__(self, seed: Iterable[Evening] = ()) -> None:
        self._evenings: dict[EveningId, Evening] = {evening.id: evening for evening in seed}

    def get(self, evening_id: EveningId) -> Evening | None:
        return self._evenings.get(evening_id)
