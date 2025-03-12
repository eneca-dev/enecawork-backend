from uuid import UUID
from pydantic import BaseModel, Field


class ProjectResponse(BaseModel):
    project_id: UUID = Field(..., alias="id")
    project_name: str = Field(..., alias="name")


class SectionResponse(BaseModel):
    section_id: UUID = Field(..., alias="id")
    project_id: UUID
    section_name: str = Field(..., alias="name")
