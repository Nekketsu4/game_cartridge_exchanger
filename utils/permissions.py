# from fastapi import HTTPException

from api.schemas import GetUser
from database.models import RolesCredentions


async def user_permissions(target_user: GetUser, current_user: GetUser) -> bool:
    # if RolesCredentions.ROLE_SUPER_ADMIN in current_user.roles:
    #     raise HTTPException(
    #         status_code=403, detail="Forbidden"
    #     )
    if target_user != current_user:
        if not {
            RolesCredentions.ROLE_ADMIN,
            RolesCredentions.ROLE_SUPER_ADMIN,
        }.intersection(current_user["roles"]):
            return False
        if (
            RolesCredentions.ROLE_ADMIN in target_user.roles
            and RolesCredentions.ROLE_SUPER_ADMIN in current_user.roles
        ):
            return False
    return True
