from enum import Enum

from api.schemas import GetUser


class RolesCredentions(str, Enum):
    ROLE_USER = "ROLE_USER"
    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_SUPER_ADMIN = "ROLE_SUPER_ADMIN"


async def user_permissions(target_user: GetUser, current_user: GetUser) -> bool:
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
