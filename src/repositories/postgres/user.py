from sqlalchemy import select

from src.database.postgres.connection import async_session
from src.database.postgres.models import User


class UserRepository:
    @staticmethod
    async def create_user(telegram_id: int):
        async with async_session() as session:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def check_if_user_exists(telegram_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(User).
                where(User.telegram_id == telegram_id)
            )
            if result.scalar_one_or_none():
                return True
            return False

    @staticmethod
    async def get_all_users():
        async with async_session() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    @staticmethod
    async def get_user(telegram_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(User).
                where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def delete_user(telegram_id: int):
        async with async_session() as session:
            user = await UserRepository.get_user(telegram_id=telegram_id)
            if not user:
                raise Exception(
                    f"User with telegram_id {telegram_id} doesn't exist"
                )
            await session.delete(user)
            await session.commit()
