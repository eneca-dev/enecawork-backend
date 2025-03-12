from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import auth_router, user_router, digest_router
from app.routes.assignments import router as assignments_router
from app.routes.projects import router as projects_router
from app.exceptions.digest import (
    DigestBaseException,
    DigestNotFoundException,
    DigestAuthError,
    DigestDatabaseError,
    DigestValidationError,
)
from app.exceptions.assignments import (
    AssignmentBaseException,
    AssignmentNotFoundException,
    ProjectNotFoundException,
    SectionNotFoundException,
    AssignmentValidationError,
    AssignmentDatabaseError,
    AssignmentAuthError,
)
import logging
import sys


# Setup logging with console output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


# Create a test log to check the logging functionality
logger = logging.getLogger(__name__)
logger.info("Application starting...")

app = FastAPI(title="Backend for eneca.work")


# Добавляем обработчик исключений для модуля digest
@app.exception_handler(DigestBaseException)
async def digest_exception_handler(request: Request, exc: DigestBaseException):
    if isinstance(exc, DigestNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )
    elif isinstance(exc, DigestAuthError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)}
        )
    elif isinstance(exc, DigestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )
    elif isinstance(exc, DigestDatabaseError):
        # Логируем реальную ошибку, но клиенту отправляем общее сообщение
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Не удалось выполнить операцию"},
        )

    # Если не нашли подходящий обработчик
    logger.error(f"Unhandled digest error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Неизвестная ошибка"},
    )


# Отдельный обработчик для ProjectNotFoundException
@app.exception_handler(ProjectNotFoundException)
async def project_not_found_handler(request: Request,
                                    exc: ProjectNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


# Добавляем обработчик исключений для модуля assignments
@app.exception_handler(AssignmentBaseException)
async def assignment_exception_handler(request: Request,
                                       exc: AssignmentBaseException):
    if isinstance(exc, AssignmentNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )
    elif isinstance(exc, SectionNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )
    elif isinstance(exc, AssignmentAuthError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)}
        )
    elif isinstance(exc, AssignmentValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )
    elif isinstance(exc, AssignmentDatabaseError):
        # Логируем реальную ошибку, но клиенту отправляем общее сообщение
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ошибка при работе с базой данных"},
        )

    # Если не нашли подходящий обработчик
    logger.error(f"Unhandled assignment error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Неизвестная ошибка"},
    )


# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router, tags=["auth"])
app.include_router(user_router, tags=["users"])
app.include_router(digest_router, prefix="/api", tags=["digest"])
app.include_router(assignments_router, prefix="/api")
app.include_router(projects_router, prefix="/api")


# Server health check
@app.get("/")
async def health_check():
    return {"status": "healthy"}
