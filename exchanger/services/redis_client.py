import redis.asyncio as redis

async def get_redis():
    return redis.from_url("redis://redis:6379", decode_responses=True)
