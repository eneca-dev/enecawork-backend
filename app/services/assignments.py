from uuid import UUID
from datetime import datetime
from typing import List
import logging
from supabase import Client
from app.schemas.assignments import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentStatusUpdate,
    AssignmentResponse,
)

logger = logging.getLogger(__name__)


class AssignmentServices:
    @staticmethod
    def get_project_assignments(
        supabase: Client, project_id: UUID
    ) -> List[AssignmentResponse]:
        try:
            response = (
                supabase.table("assignments")
                .select("*")
                .eq("project_id", str(project_id))
                .execute()
            )
            return [AssignmentResponse(**item) for item in response.data]
        except Exception as e:
            logger.error(f"Error getting assignments: {str(e)}")
            raise

    @staticmethod
    def create_assignment(
        supabase: Client, project_id: UUID, user_id: UUID, assignment: AssignmentCreate
    ) -> AssignmentResponse:
        try:
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

            response = supabase.table("assignments").insert(assignment_data).execute()
            return AssignmentResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating assignment: {str(e)}")
            raise

    @staticmethod
    def update_assignment(
        supabase: Client,
        assignment_id: UUID,
        user_id: UUID,
        update_data: AssignmentUpdate,
    ) -> AssignmentResponse:
        try:
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
            return AssignmentResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error updating assignment: {str(e)}")
            raise

    @staticmethod
    def update_assignment_status(
        supabase: Client,
        assignment_id: UUID,
        status_update: AssignmentStatusUpdate,
        user_id: UUID,
    ) -> bool:
        try:
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
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error updating assignment status: {str(e)}")
            raise

    @staticmethod
    def delete_assignment(supabase: Client, assignment_id: UUID) -> bool:
        try:
            response = (
                supabase.table("assignments")
                .delete()
                .eq("id", str(assignment_id))
                .execute()
            )
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting assignment: {str(e)}")
            raise
