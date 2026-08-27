from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

# Fetch the global settings instance containing DATABASE_URL
settings = get_settings()

# 1. Create the asynchronous database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to True during development to see raw SQL queries in logs
)

# 2. Create a session factory for generating database sessions asynchronously
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 3. Define the DeclarativeBase class for all ORM models to inherit from
class Base(DeclarativeBase):
    pass