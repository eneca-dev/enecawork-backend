from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import auth_router, user_router, digest_router
from app.exceptions.digest import (
    DigestBaseException,
    DigestNotFoundException,
    DigestAuthError,
    DigestDatabaseError,
    DigestValidationError,
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


# Добавляем обработчик исключений
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


# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router, tags=["auth"])
app.include_router(user_router, tags=["users"])
app.include_router(digest_router, prefix="/api", tags=["digest"])


# Server health check
@app.get("/")
async def health_check():
    return {"status": "healthy"}
