import uuid
from typing import List
from api.schemas import GetUser, CreateUser, UpdateUser, DeleteUser
from api.crud import UserView
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import UUID
from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException

from database.models import User
from database.session import get_async_session


async def _create_new_user(body: CreateUser, session: AsyncSession) -> GetUser:
    async with session.begin():
        user_view = UserView(session)
        user = await user_view.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email
        )
        # return GetUser(
        #     user_id=user.user_id,
        #     name=user.name,
        #     surname=user.surname,
        #     email=user.email,
        #     is_active=user.is_active
        # )
        return GetUser.model_validate(user).model_dump() #аналогичен закоментированному коду выше


async def _get_users(session: AsyncSession) -> List[GetUser]:
    async with session.begin():
        user_view = UserView(session)
        users = await user_view.get_all_users()
        return [GetUser.model_validate(user).model_dump() for user in users]


async def _get_user_by_id(user_id: UUID, session: AsyncSession) -> User:
    async with session.begin():
        user_view = UserView(session)
        user = await user_view.get_user_by_id(user_id=user_id)
        return GetUser.model_validate(user).model_dump()


async def _update_user(body, user_id: UUID, session: AsyncSession):
    async with session.begin():
        # value_model = create_model(
        #     'ValueModel',
        #     name=(str, ...),
        #     surname=(str, ...),
        #     email=(EmailStr, ...)
        # )
        user_view = UserView(session)
        await user_view.update_user(
            user_id=user_id,
            **body.model_dump(exclude_unset=True)
        )
        # return {"response": f"success update for {body.name}"}


async def _delete_user(user_id: UUID, session: AsyncSession):
    async with session.begin():
        user_view = UserView(session)
        deleted_id = await user_view.delete_user(user_id=user_id)
        return {"response": f"User with ID:{deleted_id} has been deleted"}


user_router = APIRouter()

@user_router.post("/", response_model=GetUser)
async def create_user(body: CreateUser, session: AsyncSession = Depends(get_async_session)):
    try:
        return await _create_new_user(body, session)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=f'User already exists')


@user_router.get("/", response_model=List[GetUser])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    return await _get_users(session)

@user_router.get("/{user_id}", response_model=GetUser)
async def get_user_by_id(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await _get_user_by_id(user_id, session)


@user_router.patch("/{user_id}")
async def update_user(body: UpdateUser, user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    updated_data = body.model_dump(exclude_unset=True)
    if updated_data == {}:
        raise HTTPException(status_code=422, detail="Body is empty")
    await _update_user(body, user_id, session)
    return {"response": f"success update for {body.name}"}

@user_router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await _delete_user(user_id, session)