import logging
from datetime import date
from typing import List
from supabase import Client
from app.schemas.digest import ProjectInfo, DigestResponse
from app.exceptions.digest import DigestNotFoundException, ProjectNotFoundException, DigestDatabaseError, DigestAuthError, DigestClientError, DigestValidationError
from postgrest.exceptions import APIError
from supabase.lib.client_options import ClientException
from gotrue.errors import AuthApiError

logger = logging.getLogger(__name__)

class DigestServices:
    @staticmethod
    def get_unique_projects(supabase: Client) -> List[ProjectInfo]:
        try:
            query = supabase.from_('digest_reports').select(
                'project_id, project_name, project_manager, project_manager_email'
            ).execute()
            
            # Создаем множество для хранения уникальных проектов
            unique_projects = {}
            for item in query.data:
                project_id = item['project_id']
                if project_id not in unique_projects:
                    unique_projects[project_id] = ProjectInfo(**item)
            
            if not unique_projects:
                raise ProjectNotFoundException(0)  # 0 означает, что не найдено ни одного проекта
            
            return list(unique_projects.values())
            
        except APIError as e:
            # Ошибки PostgREST API (проблемы с запросами к БД)
            logger.error(f"PostgREST API error: {str(e)}")
            raise DigestDatabaseError("получении списка проектов", str(e))
            
        except AuthApiError as e:
            # Ошибки аутентификации
            logger.error(f"Authentication error: {str(e)}")
            raise DigestAuthError("проверке доступа к данным", str(e))
            
        except ClientException as e:
            # Ошибки клиента Supabase
            logger.error(f"Supabase client error: {str(e)}")
            raise DigestClientError("работе с Supabase", str(e))
            
        except ValueError as e:
            # Ошибки валидации данных
            logger.error(f"Data validation error: {str(e)}")
            raise DigestValidationError("обработке данных проектов", str(e))
    
    @staticmethod
    def get_digest(
        supabase: Client,
        project_id: int,
        digest_date: date
    ) -> DigestResponse:
        try:
            query = supabase.from_('digest_reports').select(
                'digest_text'
            ).filter('project_id', 'eq', project_id).filter(
                'digest_date', 'eq', digest_date.isoformat()
            ).execute()
            
            if not query.data:
                raise DigestNotFoundException(project_id, digest_date)
            
            return DigestResponse(digest_text=query.data[0]['digest_text'])
            
        except APIError as e:
            # Ошибки PostgREST API
            logger.error(f"PostgREST API error: {str(e)}")
            raise DigestDatabaseError("получении текста дайджеста", str(e))
            
        except AuthApiError as e:
            # Ошибки аутентификации
            logger.error(f"Authentication error: {str(e)}")
            raise DigestAuthError("проверке доступа к дайджесту", str(e))
            
        except ClientException as e:
            # Ошибки клиента Supabase
            logger.error(f"Supabase client error: {str(e)}")
            raise DigestClientError("работе с Supabase", str(e))
            
        except ValueError as e:
            # Ошибки валидации данных
            logger.error(f"Data validation error: {str(e)}")
            raise DigestValidationError("обработке данных дайджеста", str(e)) 