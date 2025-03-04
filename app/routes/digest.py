from fastapi import APIRouter, Depends, status
from supabase import Client
from typing import List
from app.database import get_supabase
from app.services.digest import DigestServices
from app.schemas.digest import ProjectInfo, DigestRequest, DigestResponse

digest_router = APIRouter(
    prefix='/digest',
    tags=['digest'],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': 'Internal server error',
            'content': {
                'application/json': {
                    'example': {'detail': 'Internal server error'}
                }
            }
        }
    }
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