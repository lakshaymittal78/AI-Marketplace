from redis import asyncio as aioredis
import os

# Docker injects REDIS_URL via environment; fallback for local dev
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = aioredis.from_url(redis_url)

async def save_to_redis(key, value):
    await redis_client.set(key, value,ex=86400)

async def get_from_redis(key):
    return await redis_client.get(key)

async def delete_from_redis(key):
    await redis_client.delete(key)