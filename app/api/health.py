from fastapi import APIRouter

router = APIRouter()

@router.get("/health",tags=["Health Check"])
async def health_check()-> dict[str, str]:
    """Health check endpoint to verify the service is running"""
    return {"status": "healthy"} 