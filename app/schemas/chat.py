from pydantic import BaseModel, field_validator
from app.guardrails.prompt_injection import contains_injection_attempt

class ChatRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def check_for_injection(cls, v: str) -> str:
        if contains_injection_attempt(v):
            raise ValueError(
                "Your message contains content that cannot be processed. Please rephrase your question."
            )
        return v

class ChatResponse(BaseModel):
    answer: str
    results: list[dict]