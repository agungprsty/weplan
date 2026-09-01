import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_superadmin: bool = False
    provider: str = "email"
    avatar_url: str | None = None
    email_verified: bool = False
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
