from fastapi import APIRouter, Depends, status
from supabase import Client
from typing import List, Dict
from app.database import get_supabase
from app.services.digest import DigestServices
from app.schemas.digest import ProjectInfo, DigestRequest, DigestResponse
from fastapi.responses import JSONResponse
from app.exceptions.digest import (
    DigestBaseException,
    DigestDatabaseError,
    DigestAuthError,
    DigestClientError,
    DigestValidationError,
    DigestNotFoundException
)
import logging

logger = logging.getLogger(__name__)

# Определяем базовые сообщения об ошибках
ERROR_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: ('Bad request', 'Неверный запрос'),
    status.HTTP_401_UNAUTHORIZED: ('Unauthorized', 'Ошибка авторизации'),
    status.HTTP_404_NOT_FOUND: ('Not found', 'Дайджест не найден')
}

# Создаем ответы для документации API из базовых сообщений
ERROR_RESPONSES = {
    status_code: {
        'description': description,
        'content': {
            'application/json': {
                'example': {'detail': message}
            }
        }
    }
    for status_code, (description, message) in ERROR_MESSAGES.items()
}

# Определяем маппинг исключений на HTTP-статусы
ERROR_HANDLERS = {
    DigestNotFoundException: status.HTTP_404_NOT_FOUND,
    DigestAuthError: status.HTTP_401_UNAUTHORIZED,
    DigestValidationError: status.HTTP_400_BAD_REQUEST,
    (DigestDatabaseError, DigestClientError): status.HTTP_400_BAD_REQUEST
}

digest_router = APIRouter(
    prefix='/digest',
    tags=['digest'],
    responses=ERROR_RESPONSES
)

@digest_router.get(
    '/projects',
    response_model=List[ProjectInfo],
    status_code=status.HTTP_200_OK,
    summary='Get unique projects list',
    description='Get list of unique projects with their managers'
)
def get_projects(
    supabase: Client = Depends(get_supabase)
) -> List[ProjectInfo]:
    return DigestServices.get_unique_projects(supabase=supabase)

@digest_router.post(
    '/markdown',
    response_model=DigestResponse,
    status_code=status.HTTP_200_OK,
    summary='Get digest markdown',
    description='Get digest markdown by project ID and date',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Digest not found',
            'content': {
                'application/json': {
                    'example': {'detail': 'Digest not found'}
                }
            }
        }
    }
)
def get_digest_text(
    request: DigestRequest,
    supabase: Client = Depends(get_supabase)
) -> DigestResponse:
    return DigestServices.get_digest(
        supabase=supabase,
        project_id=request.project_id,
        digest_date=request.digest_date
    )

@digest_router.exception_handler(DigestBaseException)
async def digest_exception_handler(request, exc: DigestBaseException):
    # Находим подходящий статус код
    for exc_type, status_code in ERROR_HANDLERS.items():
        if isinstance(exc, exc_type):
            # Для внутренних ошибок логируем детали
            if isinstance(exc, (DigestDatabaseError, DigestClientError)):
                logger.error(f"Internal error: {str(exc)}")
            
            # Получаем сообщение из ERROR_MESSAGES
            _, message = ERROR_MESSAGES[status_code]
            return JSONResponse(
                status_code=status_code,
                content={'detail': message}
            ) 