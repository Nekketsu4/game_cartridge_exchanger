from typing import Union

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RolesCredentions, User

# BUSINESS LOGIC


class UserView:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: EmailStr,
        hashed_password: str,
        roles: list[RolesCredentions],
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
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
        return user

    async def get_user_by_email(self, email: str):
        result = await self.session.execute(select(User).filter_by(email=email))
        user = result.scalar_one_or_none()
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
            return user.user_id
        else:
            return None
