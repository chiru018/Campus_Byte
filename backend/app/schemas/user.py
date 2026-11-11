import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="Unique email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Optional contact phone number")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Role within Campus Byte platform")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="Plaintext password for registration")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int

