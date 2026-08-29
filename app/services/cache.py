import redis.asyncio as redis
import hashlib
import json

_redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

def _cache_key(question: str) -> str:
    normalized = question.strip().lower()
    return "chat_cache:" + hashlib.sha256(normalized.encode()).hexdigest()

async def get_cached_answer(question: str) -> str | None:
    key = _cache_key(question)
    return await _redis_client.get(key)

async def set_cached_answer(question: str, answer: str, ttl_seconds: int = 3600) -> None:
    key = _cache_key(question)
    await _redis_client.set(key, answer, ex=ttl_seconds)