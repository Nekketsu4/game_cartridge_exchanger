import uuid
from typing import List

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import UserView
from api.login_handler import get_user_by_token
from api.schemas import CreateUser, GetFullUser, GetUser, UpdateUser
from database.models import RolesCredentions
from database.session import get_async_session
from security.hashing import get_password_hash
from utils.permissions import user_permissions

user_router = APIRouter()


async def _create_new_user(body: CreateUser, session: AsyncSession) -> GetUser:
    async with session.begin():
        user_view = UserView(session)
        user = await user_view.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=get_password_hash(body.password),
            roles=[
                RolesCredentions.ROLE_USER,
            ],
        )
        # return GetUser(
        #     user_id=user.user_id,
        #     name=user.name,
        #     surname=user.surname,
        #     email=user.email,
        #     is_active=user.is_active
        # )
        return GetUser.model_validate(user).model_dump()


async def _get_users(session: AsyncSession) -> List[GetUser]:
    async with session.begin():
        user_view = UserView(session)
        users = await user_view.get_all_users()
        return [GetUser.model_validate(user).model_dump() for user in users]


async def _get_user_by_id(user_id: UUID, session: AsyncSession) -> GetFullUser:
    async with session.begin():
        user_view = UserView(session)
        user = await user_view.get_user_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User was not found")
        return GetFullUser.model_validate(user).model_dump()


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
            user_id=user_id, **body.model_dump(exclude_unset=True)
        )
        # return {"response": f"success update for {body.name}"}


async def _delete_user(user_id: UUID, session: AsyncSession):
    async with session.begin():
        user_view = UserView(session)
        deleted_id = await user_view.delete_user(user_id=user_id)
        if deleted_id:
            return {"response": f"User with ID:{deleted_id} has been deleted"}
        return None


@user_router.post("/", response_model=GetUser)
async def create_user(
    body: CreateUser, session: AsyncSession = Depends(get_async_session)
):
    try:
        return await _create_new_user(body, session)
    except IntegrityError:
        raise HTTPException(status_code=500, detail="User already exists")


@user_router.get("/", response_model=List[GetUser])
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_user_by_token),
):
    return await _get_users(session)


@user_router.get("/{user_id}", response_model=GetUser)
async def get_user_by_id(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_user_by_token),
):
    return await _get_user_by_id(user_id, session)


@user_router.patch("/{user_id}")
async def update_user(
    body: UpdateUser,
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_user_by_token),
):
    updated_data = body.model_dump(exclude_unset=True)
    if updated_data == {}:
        raise HTTPException(status_code=422, detail="Body is empty")
    user_for_update = await _get_user_by_id(user_id, session)
    if user_for_update is None:
        raise HTTPException(status_code=404, detail="User was not found")
    perm = await user_permissions(
        target_user=user_for_update, current_user=current_user
    )
    if not perm:
        raise HTTPException(status_code=403, detail="Forbidden")
    await _update_user(body, user_id, session)

    return {"response": f"success update for {body.name}"}


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_user_by_token),
):
    user_for_delete = await _get_user_by_id(user_id, session)
    if user_for_delete is None:
        raise HTTPException(status_code=404, detail="User was not found")
    if not await user_permissions(
        target_user=user_for_delete, current_user=current_user
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    user = await _delete_user(user_id, session)
    return user


# @user_router.patch("/admin_privilege")
# async def promote_to_admin_privilege(
#         user_id: UUID,
#         db: AsyncSession = Depends(get_async_session),
#         current_user = Depends(get_user_by_token)
# ):
#     if not current_user.
