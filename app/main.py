from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.echo import router as echo_router
app =  FastAPI(title="Agentic RAG Widget API",version="1.0.0")


app.include_router(health_router)
app.include_router(echo_router)    