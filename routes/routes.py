from fastapi.routing import APIRouter

from api.handlers import user_router
from api.login_handler import login_router

main_router = APIRouter()

main_router.include_router(user_router, prefix="/user", tags=["user"])
main_router.include_router(login_router, prefix="/login", tags=["login"])
