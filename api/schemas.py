import re
import uuid

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

# SCHEMAS

LETTER_MATCH = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TuneModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GetUser(TuneModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool
    roles: list


class GetFullUser(GetUser):
    hashed_password: str


class UpdateUser(BaseModel):
    # ключевой момент записи type | None = None
    # чтобы заработал функционал частичного апдейта данных
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None


class DeleteUser(BaseModel):
    user_id: uuid.UUID


class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH.match(value):
            raise HTTPException(status_code=422, detail="Имя должно содержать буквы")
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH.match(value):
            raise HTTPException(
                status_code=422, detail="Фамилия должна содержать буквы"
            )
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
