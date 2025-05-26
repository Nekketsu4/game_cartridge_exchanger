from fastapi import Depends
from fastapi.routing import APIRouter
from api.handlers import user_router


main_router = APIRouter()

main_router.include_router(user_router, prefix="/user", tags=["user"])