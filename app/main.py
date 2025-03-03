from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_router, user_router
import logging
import sys


# Setup logging with console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


# Create a test log to check the logging functionality
logger = logging.getLogger(__name__)
logger.info("Application starting...")

app = FastAPI(
    title='Backend for eneca.work'
)


# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Include routers
app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(user_router, prefix='/users', tags=['users'])


# Server health check
@app.get('/')
async def health_check():
    return {'status': 'healthy'} 