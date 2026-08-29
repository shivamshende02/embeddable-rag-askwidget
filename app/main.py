from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.echo import router as echo_router
from app.core.config import get_settings
from app.api import documents
from app.api import chat
from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, version="1.0.0")

# Attach the shared limiter to app state and register rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(health_router)
app.include_router(echo_router)  
app.include_router(documents.router)  
app.include_router(chat.router)