from fastapi import APIRouter, Depends, status
from supabase import Client
from typing import List
from uuid import UUID
from app.database import get_supabase
from app.dependencies.auth import get_current_user_id
from app.services.projects import ProjectServices
from app.schemas.projects import ProjectResponse, SectionResponse

router = APIRouter(tags=["projects"])


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Ошибка аутентификации"}},
)
async def get_projects(
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """Получить список всех проектов"""
    return ProjectServices.get_projects(supabase)


@router.get(
    "/projects/{project_id}/sections",
    response_model=List[SectionResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Ошибка аутентификации"},
        404: {"description": "Проект не найден"},
    },
)
async def get_project_sections(
    project_id: UUID,
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """Получить список всех секций проекта"""
    return ProjectServices.get_project_sections(supabase, project_id)
