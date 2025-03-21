from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from src.database.postgres.connection import async_session
from src.database.postgres.models import UserChannelSubscription


class UserNewsSubscriptionRepository:
    @staticmethod
    async def add_subscription(user_id: int, channel_id: int, notification_period: int):
        async with async_session() as session:
            subscription = UserChannelSubscription(
                user_id=user_id,
                channel_id=channel_id,
                notifications_period=notification_period
            )
            session.add(subscription)
            await session.commit()

    @staticmethod
    async def update_subscription(
            user_id: int,
            channel_id: int,
            new_notification_period: int
    ):
        async with async_session() as session:
            await session.execute(
                (
                    update(UserChannelSubscription)
                    .where(UserChannelSubscription.user_id == user_id)
                    .where(UserChannelSubscription.channel_id == channel_id)
                    .values(notifications_period=new_notification_period)
                )
            )
            await session.commit()

    @staticmethod
    async def get_subscription(user_id: int, channel_id: int):
        async with async_session() as session:
            result = await session.execute(select(UserChannelSubscription).where(
                (UserChannelSubscription.user_id == user_id) &
                (UserChannelSubscription.channel_id == channel_id))
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_subscriptions_by_user(user_id: int):
        async with async_session() as session:
            result = await session.execute(select(UserChannelSubscription).where(
                (UserChannelSubscription.user_id == user_id)
            ).options(
                joinedload(UserChannelSubscription.channel))
            )
            subscriptions = result.unique().scalars().all()
            return subscriptions

    @staticmethod
    async def delete_subscription(user_id: int, channel_id: int):
        async with async_session() as session:
            result = await UserNewsSubscriptionRepository.get_subscription(
                user_id=user_id,
                channel_id=channel_id
            )
            if not result:
                raise Exception(
                    f"No subscription found for "
                    f"user_id {user_id} channel_id {channel_id}"
                )
            await session.delete(result)
            await session.commit()

    @staticmethod
    async def delete_subscriptions_by_user(user_id: int):
        async with async_session() as session:
            results = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
                user_id=user_id
            )
            if not results:
                raise Exception(
                    f"No subscription found for user_id {user_id}"
                )
            for result in results:
                await session.delete(result)
            await session.commit()
