from pydantic import BaseModel
from datetime import date


class ProjectInfo(BaseModel):
    project_id: int
    project_name: str
    project_manager: str
    project_manager_email: str


class DigestRequest(BaseModel):
    project_id: int
    digest_date: date


class DigestResponse(BaseModel):
    digest_text: str
