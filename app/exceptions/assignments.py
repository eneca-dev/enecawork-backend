from fastapi import HTTPException, status


class AssignmentBaseException(HTTPException):
    """Базовое исключение для модуля assignments"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class AssignmentNotFoundException(AssignmentBaseException):
    """Исключение, когда задание не найдено"""
    def __init__(self, assignment_id: str):
        super().__init__(f"Задание с ID {assignment_id} не найдено")
        self.status_code = status.HTTP_404_NOT_FOUND


class ProjectNotFoundException(AssignmentBaseException):
    """Исключение, когда проект не найден"""
    def __init__(self, project_id: str):
        super().__init__(f"Проект с ID {project_id} не найден")
        self.status_code = status.HTTP_404_NOT_FOUND


class SectionNotFoundException(AssignmentBaseException):
    """Исключение, когда секция не найдена"""
    def __init__(self, section_id: str):
        super().__init__(f"Секция с ID {section_id} не найдена")
        self.status_code = status.HTTP_404_NOT_FOUND


class AssignmentValidationError(AssignmentBaseException):
    """Исключение при ошибке валидации данных задания"""
    def __init__(self, detail: str):
        super().__init__(f"Ошибка валидации данных задания: {detail}")
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class AssignmentDatabaseError(AssignmentBaseException):
    """Исключение при ошибке базы данных"""
    def __init__(self, operation: str, detail: str):
        super().__init__(f"Ошибка базы данных при {operation}: {detail}")


class AssignmentAuthError(AssignmentBaseException):
    """Исключение при ошибке авторизации"""
    def __init__(self, operation: str):
        super().__init__(f"Ошибка авторизации при {operation}")
        self.status_code = status.HTTP_401_UNAUTHORIZED
