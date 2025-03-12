from uuid import UUID
from typing import List
import logging
from supabase import Client
from postgrest.exceptions import APIError
from app.schemas.projects import ProjectResponse, SectionResponse
from app.exceptions.assignments import ProjectNotFoundException

logger = logging.getLogger(__name__)


class ProjectServices:
    @staticmethod
    def get_projects(supabase: Client) -> List[ProjectResponse]:
        try:
            response = (
                supabase.table("projects").select("id, name, ws_project_id").execute()
            )
            logger.info(f"Projects response: {response.data}")
            return [ProjectResponse(**item) for item in response.data]
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise

    @staticmethod
    def get_project_sections(
        supabase: Client, project_id: UUID
    ) -> List[SectionResponse]:
        try:
            # Сначала получаем ws_project_id для данного project_id
            try:
                project = (
                    supabase.table("projects")
                    .select("ws_project_id")
                    .eq("id", str(project_id))
                    .single()
                    .execute()
                )

                if not project.data:
                    logger.info(f"Проект с ID {project_id} не найден")
                    raise ProjectNotFoundException(str(project_id))
            except APIError as e:
                # Если ошибка при проверке проекта, считаем что проект не найден
                logger.error(f"Ошибка при проверке проекта: {str(e)}")
                raise ProjectNotFoundException(str(project_id))

            ws_project_id = project.data["ws_project_id"]

            # Теперь получаем секции по ws_project_id
            response = (
                supabase.table("sections")
                .select("id, ws_project_id, name")
                .eq("ws_project_id", ws_project_id)
                .execute()
            )

            logger.info(f"Sections response: {response.data}")

            # Преобразуем ws_project_id в project_id для ответа
            sections = []
            for item in response.data:
                section_data = {
                    "id": item["id"],
                    "project_id": project_id,  # Используем UUID проекта
                    "name": item["name"],
                }
                sections.append(SectionResponse(**section_data))

            return sections
        except ProjectNotFoundException:
            # Пробрасываем исключение о ненайденном проекте выше
            raise
        except Exception as e:
            logger.error(f"Error getting sections: {str(e)}")
            raise
