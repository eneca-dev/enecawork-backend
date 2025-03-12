from fastapi import APIRouter, Depends, status
from supabase import Client
from typing import List
from app.database import get_supabase
from app.services.digest import DigestServices
from app.schemas.digest import ProjectInfo, DigestResponse
from app.exceptions.digest import (
    DigestDatabaseError,
    DigestAuthError,
    DigestClientError,
    DigestValidationError,
    DigestNotFoundException,
)
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# Определяем базовые сообщения об ошибках
ERROR_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: ("Bad request", "Неверный запрос"),
    status.HTTP_401_UNAUTHORIZED: ("Unauthorized", "Ошибка авторизации"),
    status.HTTP_404_NOT_FOUND: ("Not found", "Дайджест не найден"),
}

# Создаем ответы для документации API из базовых сообщений
ERROR_RESPONSES = {
    status_code: {
        "description": description,
        "content": {"application/json": {"example": {"detail": message}}},
    }
    for status_code, (description, message) in ERROR_MESSAGES.items()
}

# Определяем маппинг исключений на HTTP-статусы
ERROR_HANDLERS = {
    DigestNotFoundException: status.HTTP_404_NOT_FOUND,
    DigestAuthError: status.HTTP_401_UNAUTHORIZED,
    DigestValidationError: status.HTTP_400_BAD_REQUEST,
    (DigestDatabaseError, DigestClientError): status.HTTP_400_BAD_REQUEST,
}

digest_router = APIRouter(prefix="/digest",
                          tags=["digest"],
                          responses=ERROR_RESPONSES)


@digest_router.get(
    "/projects",
    response_model=List[ProjectInfo],
    status_code=status.HTTP_200_OK,
    summary="Get unique projects list",
    description="""
    Get list of unique projects with their managers
    """,
)
def get_projects(supabase: Client = Depends(get_supabase)) -> List[ProjectInfo]:
    return DigestServices.get_unique_projects(supabase=supabase)


@digest_router.get(
    "/markdown/{project_id}",
    response_model=DigestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get digest markdown",
    description="""
    Get digest markdown by project ID and date.
    If date is not provided, the current date will be used.
  
    **Examples:**
    - `/api/markdown/123` → gets digest for yesterday
    - `/api/markdown/123?digest_date=2024-03-20` → gets digest for the specified date
    """,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Дайджест не найден",
            "content": {
                "application/json": {"example": {"detail": "Дайджест не найден"}}
            },
        }
    },
)
def get_digest_text(
    project_id: int,
    digest_date: date = date.today() - timedelta(days=1),  # вчерашняя дата
    supabase: Client = Depends(get_supabase),
) -> DigestResponse:
    return DigestServices.get_digest(
        supabase=supabase, project_id=project_id, digest_date=digest_date
    )
