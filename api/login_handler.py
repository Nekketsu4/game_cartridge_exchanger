from datetime import timedelta
from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

import config
from api.crud import UserView
from api.schemas import GetFullUser, Token
from database.models import User
from database.session import get_async_session
from security.create_token import create_access_token
from security.hashing import verify_password

login_router = APIRouter()


async def _get_user_auth_email(email: str, session: AsyncSession) -> GetFullUser:
    async with session.begin():
        user_view = UserView(session)
        user = await user_view.get_user_by_email(email=email)
        dct = GetFullUser.model_validate(user).model_dump()
        return GetFullUser(**dct)


async def authenticate_user(
    email: str, password: str, session: AsyncSession
) -> Union[GetFullUser, None]:
    user = await _get_user_auth_email(email, session)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@login_router.post("/token", response_model=Token)
async def get_login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token_expire = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        payload={"sub": user.email, "name": user.name, "surname": user.surname},
        expire_time=access_token_expire,
    )
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_user_by_token(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    exception_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="User unauthorized"
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exception_401
    except JWTError:
        raise exception_401
    user = await _get_user_auth_email(username, session)
    if user is None:
        raise exception_401
    return user


@login_router.get("/test_auth")
async def get_user_info_by_jwt(user: User = Depends(get_user_by_token)):
    return {"Success": True, "user": user}
