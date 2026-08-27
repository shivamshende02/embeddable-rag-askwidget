from fastapi import FastAPI

app =  FastAPI(title="Agentic RAG Widget API",version="1.0.0")

@app.get("/health",tags=["Health Check"])
async def health_check():
    """Health check endpoint to verify the service is running"""
    return {"status": "healthy"}