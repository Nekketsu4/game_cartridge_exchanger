from typing import Union

from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import UUID
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

# BUSINESS LOGIC

class UserView:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
            self, name: str, surname: str, email: EmailStr
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email
        )
        self.session.add(new_user)
        await self.session.flush()
        return new_user

    async def get_all_users(self):
        result = await self.session.execute(select(User))
        users = result.scalars().all()
        return users

    async def get_user_by_id(self, user_id: UUID):
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User was not found")
        return user


    async def update_user(self, user_id: UUID, **kwargs):
        get_user = await self.session.get(User, user_id)
        for key, value in kwargs.items():
            setattr(get_user, key, value)
        await self.session.commit()

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        user = await self.session.get(User, user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
        else:
            raise HTTPException(status_code=404, detail="User was not found")
        return user.user_id