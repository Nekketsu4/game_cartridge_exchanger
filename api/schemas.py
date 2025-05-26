import re
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, constr
from fastapi.exceptions import HTTPException

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


class UpdateUser(BaseModel):
    name: str | None = None     #ключевой момент записи type | None = None чтобы заработал функционал частичного апдейта данных
    surname: str | None = None
    email: EmailStr | None = None


class DeleteUser(BaseModel):
    user_id: uuid.UUID


class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr


    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH.match(value):
            raise HTTPException(
                status_code=422, detail='Имя должно содержать буквы'
            )
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH.match(value):
            raise HTTPException(
                status_code=422, detail='Фамилия должна содержать буквы'
            )
        return value