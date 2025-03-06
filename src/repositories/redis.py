from src.database.redis.connection import redis_client


class RedisRepository:
    @staticmethod
    async def get_value(key: str = None):
        value = await redis_client.get(name=key)
        return value.decode() if value else None

    @staticmethod
    async def set_value(key: str = None, value = None) -> None:
        await redis_client.set(name=key, value=value)

    @staticmethod
    async def delete_value(key: str) -> None:
        await redis_client.delete(key)
