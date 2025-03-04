import logging
from datetime import date
from typing import List
from supabase import Client
from fastapi import HTTPException, status
from app.schemas.digest import ProjectInfo, DigestResponse

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
            
            return list(unique_projects.values())
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Database error: {str(e)}'
            )
    
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
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Digest not found'
                )
            
            return DigestResponse(digest_text=query.data[0]['digest_text'])
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Database error: {str(e)}'
            ) 