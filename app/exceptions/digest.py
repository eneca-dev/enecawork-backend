class DigestBaseException(Exception):
    """Базовый класс для исключений дайджеста"""

    pass


class DigestNotFoundException(DigestBaseException):
    """Исключение для случая, когда дайджест не найден"""

    def __init__(self, project_id: int, digest_date: str):
        self.message = (
            f"Дайджест не найден для проекта {project_id} " f"на дату {digest_date}"
        )
        super().__init__(self.message)


class ProjectNotFoundException(DigestBaseException):
    """Исключение для случая, когда проект не найден"""

    def __init__(self, project_id: int):
        self.message = f"Проект с ID {project_id} не найден"
        super().__init__(self.message)


class DigestDatabaseError(DigestBaseException):
    """Ошибка базы данных"""

    def __init__(self, operation: str, details: str):
        self.message = f"Ошибка базы данных при {operation}: {details}"
        super().__init__(self.message)


class DigestAuthError(DigestBaseException):
    """Ошибка аутентификации"""

    def __init__(self, operation: str):
        self.message = f"Ошибка аутентификации при {operation}"
        super().__init__(self.message)


class DigestClientError(DigestBaseException):
    """Ошибка клиента Supabase"""

    def __init__(self, operation: str, details: str):
        self.message = f"Ошибка клиента при {operation}: {details}"
        super().__init__(self.message)


class DigestValidationError(DigestBaseException):
    """Ошибка валидации данных"""

    def __init__(self, operation: str, details: str):
        self.message = f"Ошибка валидации при {operation}: {details}"
        super().__init__(self.message)
