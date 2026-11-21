"""HTTP layer: translates requests into the scenario and errors into status codes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from evenings.api.dependencies import get_registration_service
from evenings.domain.errors import (
    AlreadyRegistered,
    EveningAlreadyStarted,
    EveningFull,
    EveningNotFound,
    InvalidDanceRole,
)
from evenings.domain.models import (
    DanceRole,
    EveningId,
    Registration,
    RegistrationRequest,
    UserId,
)
from evenings.services.registration_service import RegistrationService

router = APIRouter(tags=["registrations"])

_STATUS_BY_ERROR = {
    EveningNotFound: 404,
    EveningAlreadyStarted: 409,
    AlreadyRegistered: 409,
    EveningFull: 409,
    InvalidDanceRole: 422,
}


class CreateRegistrationRequest(BaseModel):
    """Тело записи. Роль в паре нужна только танцевальным вечерам (AC-04.5)."""

    evening_id: str = Field(min_length=1, max_length=64)
    user_id: str = Field(min_length=1, max_length=64)
    dance_role: DanceRole | None = None


class RegistrationResponse(BaseModel):
    id: str
    evening_id: str
    user_id: str
    dance_role: DanceRole | None
    status: str


@router.post("/registrations", status_code=201, response_model=RegistrationResponse)
async def create_registration(
    payload: CreateRegistrationRequest,
    service: Annotated[RegistrationService, Depends(get_registration_service)],
) -> RegistrationResponse:
    # Путь без версии и user_id в теле запроса — временное устройство ЛР 3 и 4А:
    # версия /v1 и маркер доступа появятся в ЛР 4Б, тогда же путь меняется
    # и у HTTP-тестов.
    try:
        registration = service.create(
            RegistrationRequest(
                evening_id=EveningId(payload.evening_id),
                user_id=UserId(payload.user_id),
                dance_role=payload.dance_role or DanceRole.NONE,
            )
        )
    except tuple(_STATUS_BY_ERROR) as error:
        raise HTTPException(status_code=_STATUS_BY_ERROR[type(error)], detail=str(error)) from error

    return _to_response(registration)


def _to_response(registration: Registration) -> RegistrationResponse:
    """Внутри отсутствие роли — DanceRole.NONE, наружу показывается как null."""
    dance_role = registration.dance_role if registration.dance_role is not DanceRole.NONE else None
    return RegistrationResponse(
        id=registration.id,
        evening_id=registration.evening_id,
        user_id=registration.user_id,
        dance_role=dance_role,
        status=registration.status,
    )
