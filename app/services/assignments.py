from uuid import UUID
from datetime import datetime
from typing import List
import logging
from supabase import Client
from postgrest.exceptions import APIError
from gotrue.errors import AuthApiError
from app.schemas.assignments import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentStatusUpdate,
    AssignmentResponse,
)
from app.exceptions.assignments import (
    AssignmentNotFoundException,
    ProjectNotFoundException,
    SectionNotFoundException,
    AssignmentValidationError,
    AssignmentDatabaseError,
    AssignmentAuthError,
)

logger = logging.getLogger(__name__)


class AssignmentServices:
    @staticmethod
    def get_project_assignments(
        supabase: Client, project_id: UUID
    ) -> List[AssignmentResponse]:
        try:
            # Проверяем существование проекта
            try:
                project = (
                    supabase.table("projects")
                    .select("id")
                    .eq("id", str(project_id))
                    .execute()
                )
                
                if not project.data:
                    logger.info(f"Проект с ID {project_id} не найден")
                    raise ProjectNotFoundException(str(project_id))
            except APIError as e:
                # Если ошибка при проверке проекта, считаем что проект не найден
                logger.error(f"Ошибка при проверке проекта: {str(e)}")
                raise ProjectNotFoundException(str(project_id))
                
            # Получаем задания проекта
            response = (
                supabase.table("assignments")
                .select("*")
                .eq("project_id", str(project_id))
                .execute()
            )
            
            logger.info(
                f"Получено {len(response.data)} заданий для проекта {project_id}"
            )
            return [AssignmentResponse(**item) for item in response.data]
            
        except ProjectNotFoundException:
            # Пробрасываем исключение о ненайденном проекте выше
            raise
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise AssignmentDatabaseError("получении заданий", str(e))
        except AuthApiError as e:
            logger.error(f"Auth error: {str(e)}")
            raise AssignmentAuthError("получении заданий")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise AssignmentValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AssignmentDatabaseError("получении заданий", str(e))

    @staticmethod
    def create_assignment(
        supabase: Client, project_id: UUID, user_id: UUID, assignment: AssignmentCreate
    ) -> AssignmentResponse:
        try:
            # Проверяем существование проекта
            try:
                project = (
                    supabase.table("projects")
                    .select("id")
                    .eq("id", str(project_id))
                    .execute()
                )
                
                if not project.data:
                    logger.info(f"Проект с ID {project_id} не найден")
                    raise ProjectNotFoundException(str(project_id))
            except APIError as e:
                # Если ошибка при проверке проекта, считаем что проект не найден
                logger.error(f"Ошибка при проверке проекта: {str(e)}")
                raise ProjectNotFoundException(str(project_id))
                
            # Проверяем существование секций
            from_section = (
                supabase.table("sections")
                .select("id")
                .eq("id", str(assignment.from_section_id))
                .execute()
            )
            
            if not from_section.data:
                logger.info(
                    f"Секция с ID {assignment.from_section_id} не найдена"
                )
                raise SectionNotFoundException(str(assignment.from_section_id))
                
            to_section = (
                supabase.table("sections")
                .select("id")
                .eq("id", str(assignment.to_section_id))
                .execute()
            )
            
            if not to_section.data:
                logger.info(
                    f"Секция с ID {assignment.to_section_id} не найдена"
                )
                raise SectionNotFoundException(str(assignment.to_section_id))
            
            # Создаем задание
            assignment_data = {
                "project_id": str(project_id),
                "from_section_id": str(assignment.from_section_id),
                "to_section_id": str(assignment.to_section_id),
                "text": assignment.text,
                "link": assignment.link,
                "status": assignment.status,
                "due_date": assignment.due_date.isoformat(),
                "created_by": str(user_id),
                "created_at": datetime.utcnow().isoformat(),
            }

            response = (
                supabase.table("assignments")
                .insert(assignment_data)
                .execute()
            )
            
            if not response.data:
                raise AssignmentDatabaseError(
                    "создании задания", "Нет данных в ответе"
                )
                
            logger.info(f"Создано задание с ID {response.data[0]['id']}")
            return AssignmentResponse(**response.data[0])
            
        except (ProjectNotFoundException, SectionNotFoundException):
            # Пробрасываем исключения о ненайденных ресурсах выше
            raise
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise AssignmentDatabaseError("создании задания", str(e))
        except AuthApiError as e:
            logger.error(f"Auth error: {str(e)}")
            raise AssignmentAuthError("создании задания")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise AssignmentValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AssignmentDatabaseError("создании задания", str(e))

    @staticmethod
    def update_assignment(
        supabase: Client,
        assignment_id: UUID,
        user_id: UUID,
        update_data: AssignmentUpdate,
    ) -> AssignmentResponse:
        try:
            # Проверяем существование задания
            assignment = (
                supabase.table("assignments")
                .select("id")
                .eq("id", str(assignment_id))
                .execute()
            )
            
            if not assignment.data:
                logger.info(f"Задание с ID {assignment_id} не найдено")
                raise AssignmentNotFoundException(str(assignment_id))
                
            # Обновляем задание
            update_dict = update_data.model_dump(exclude_unset=True)

            if "due_date" in update_dict:
                update_dict["due_date"] = update_dict["due_date"].isoformat()

            update_dict["updated_by"] = str(user_id)
            update_dict["updated_at"] = datetime.utcnow().isoformat()

            response = (
                supabase.table("assignments")
                .update(update_dict)
                .eq("id", str(assignment_id))
                .execute()
            )
            
            logger.info(f"Обновлено задание с ID {assignment_id}")
            return AssignmentResponse(**response.data[0])
            
        except AssignmentNotFoundException:
            raise
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise AssignmentDatabaseError("обновлении задания", str(e))
        except AuthApiError as e:
            logger.error(f"Auth error: {str(e)}")
            raise AssignmentAuthError("обновлении задания")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise AssignmentValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AssignmentDatabaseError("обновлении задания", str(e))

    @staticmethod
    def update_assignment_status(
        supabase: Client,
        assignment_id: UUID,
        status_update: AssignmentStatusUpdate,
        user_id: UUID,
    ) -> bool:
        try:
            # Проверяем существование задания
            assignment = (
                supabase.table("assignments")
                .select("id")
                .eq("id", str(assignment_id))
                .execute()
            )
            
            if not assignment.data:
                logger.info(f"Задание с ID {assignment_id} не найдено")
                raise AssignmentNotFoundException(str(assignment_id))
                
            # Обновляем статус задания
            response = (
                supabase.table("assignments")
                .update(
                    {
                        "status": status_update.status,
                        "updated_by": str(user_id),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", str(assignment_id))
                .execute()
            )
            
            logger.info(f"Обновлен статус задания с ID {assignment_id} на {status_update.status}")
            return bool(response.data)
            
        except AssignmentNotFoundException:
            raise
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise AssignmentDatabaseError("обновлении статуса задания", str(e))
        except AuthApiError as e:
            logger.error(f"Auth error: {str(e)}")
            raise AssignmentAuthError("обновлении статуса задания")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise AssignmentValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AssignmentDatabaseError("обновлении статуса задания", str(e))

    @staticmethod
    def delete_assignment(supabase: Client, assignment_id: UUID) -> bool:
        try:
            # Проверяем существование задания
            assignment = (
                supabase.table("assignments")
                .select("id")
                .eq("id", str(assignment_id))
                .execute()
            )
            
            if not assignment.data:
                logger.info(f"Задание с ID {assignment_id} не найдено")
                raise AssignmentNotFoundException(str(assignment_id))
                
            # Удаляем задание
            response = (
                supabase.table("assignments")
                .delete()
                .eq("id", str(assignment_id))
                .execute()
            )
            
            logger.info(f"Удалено задание с ID {assignment_id}")
            return bool(response.data)
            
        except AssignmentNotFoundException:
            raise
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise AssignmentDatabaseError("удалении задания", str(e))
        except AuthApiError as e:
            logger.error(f"Auth error: {str(e)}")
            raise AssignmentAuthError("удалении задания")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AssignmentDatabaseError("удалении задания", str(e))
