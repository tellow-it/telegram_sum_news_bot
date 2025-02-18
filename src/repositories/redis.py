from src.database.redis.connection import redis_client


class RedisRepository:
    @staticmethod
    async def get_value(key: str = None):
        return await redis_client.get(name=key)

    @staticmethod
    async def set_value(key: str = None, value: str = None) -> None:
        await redis_client.set(name=key, value=value)

    @staticmethod
    async def delete_value(key: str) -> None:
        await redis_client.delete(key)
