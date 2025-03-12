from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class AssignmentStatus(str, Enum):
    WAITING = "Ожидается"
    IN_PROGRESS = "В работе"
    COMPLETED = "Выполнено"
    CANCELLED = "Отменено"
    TRANSFERRED = "Передано"


class AssignmentBase(BaseModel):
    text: str = Field(..., description="Текст задания")
    link: Optional[str] = Field("", description="""
                                Ссылка на дополнительные материалы
                                """
                                )
    status: AssignmentStatus = Field(default=AssignmentStatus.WAITING)
    due_date: date = Field(..., description="Срок выполнения")


class AssignmentCreate(AssignmentBase):
    from_section_id: UUID
    to_section_id: UUID


class AssignmentUpdate(BaseModel):
    text: Optional[str] = None
    link: Optional[str] = None
    due_date: Optional[date] = None


class AssignmentStatusUpdate(BaseModel):
    status: AssignmentStatus


class AssignmentResponse(AssignmentBase):
    id: UUID
    project_id: UUID
    from_section_id: UUID
    to_section_id: UUID
    created_at: datetime
    created_by: UUID
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID] = None
