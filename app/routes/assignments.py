from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List
from uuid import UUID
from app.database import get_supabase
from app.dependencies.auth import get_current_user_id
from app.services.assignments import AssignmentServices
from app.schemas.assignments import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentStatusUpdate,
    AssignmentResponse,
)

router = APIRouter(tags=["assignments"])


@router.get(
    "/projects/{project_id}/assignments",
    response_model=List[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Ошибка аутентификации"},
        404: {"description": "Проект не найден"},
    },
)
async def get_project_assignments(
    project_id: UUID,
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    return AssignmentServices.get_project_assignments(supabase, project_id)


@router.post(
    "/projects/{project_id}/assignments",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Ошибка аутентификации"},
        404: {"description": "Проект не найден"},
    },
)
async def create_assignment(
    project_id: UUID,
    assignment: AssignmentCreate,
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    return AssignmentServices.create_assignment(
        supabase, project_id, current_user_id, assignment
    )


@router.patch(
    "/assignments/{assignment_id}",
    response_model=AssignmentResponse,
    responses={
        401: {"description": "Ошибка аутентификации"},
        404: {"description": "Задание не найдено"},
    },
)
async def update_assignment(
    assignment_id: UUID,
    update_data: AssignmentUpdate,
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    return AssignmentServices.update_assignment(
        supabase, assignment_id, current_user_id, update_data
    )


@router.patch(
    "/assignments/{assignment_id}/status",
    responses={
        401: {"description": "Ошибка аутентификации"},
        404: {"description": "Задание не найдено"},
    },
)
async def update_assignment_status(
    assignment_id: UUID,
    status_update: AssignmentStatusUpdate,
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    result = AssignmentServices.update_assignment_status(
        supabase, assignment_id, status_update, current_user_id
    )
    if result:
        return {"message": "Статус задания успешно обновлен"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено"
    )


@router.delete(
    "/assignments/{assignment_id}",
    responses={
        401: {"description": "Ошибка аутентификации"},
        404: {"description": "Задание не найдено"},
    },
)
async def delete_assignment(
    assignment_id: UUID,
    supabase: Client = Depends(get_supabase),
    current_user_id: UUID = Depends(get_current_user_id),
):
    result = AssignmentServices.delete_assignment(supabase, assignment_id)
    if result:
        return {"message": "Задание успешно удалено"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено"
    )
