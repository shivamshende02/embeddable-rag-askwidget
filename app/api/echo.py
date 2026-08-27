from fastapi import APIRouter
from app.schemas.example import EchoRequest, EchoResponse

router = APIRouter()


@router.post("/echo", response_model=EchoResponse)
async def echo_message(payload: EchoRequest):
    return EchoResponse(echoed=payload.message.upper())