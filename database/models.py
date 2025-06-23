import uuid
from enum import Enum

from sqlalchemy import ARRAY, Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base

# MODELS


class RolesCredentions(str, Enum):
    ROLE_USER = "ROLE_USER"
    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_SUPER_ADMIN = "ROLE_SUPER_ADMIN"


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(ARRAY(String), nullable=False)

    @property
    def is_superadmin(self):
        return RolesCredentions.ROLE_SUPER_ADMIN in self.roles

    @property
    def is_admin(self):
        return RolesCredentions.ROLE_ADMIN in self.roles

    def add_admin_privileges(self):
        if not self.is_admin:
            return self.roles + [RolesCredentions.ROLE_ADMIN]
        return None

    def remove_admin_privileges(self):
        if self.is_admin:
            return [
                role for role in self.roles if role != RolesCredentions.ROLE_SUPER_ADMIN
            ]
        return None
