from redis.asyncio import Redis
from services.configs.config import settings

redis_client = Redis.from_url(settings.REDIS_URL)


async def get_redis_client() -> Redis:
    return Redis(host="redis", port=6379, decode_responses=True)
