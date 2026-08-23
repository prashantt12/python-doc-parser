from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

"""
This module contains the repository for the user model.

The repository is responsible for interacting with the database and providing a clean interface for the rest of the application to use.
"""
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(
            User.email == email
        )
    )
    return result.scalar_one_or_none()

"""
Create a new user in the database.
"""
async def create_user(session: AsyncSession, email: str) -> User:
    user = User(email = email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

"""
Get or create a demo user in the database.
"""
async def get_or_create_demo_user(session: AsyncSession, email: str) -> User:
    user = await get_user_by_email(session, email)
    if user:
        return user
    return await create_user(session, email)