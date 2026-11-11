import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.enums import UserRole, VehicleType
from app.schemas.user import UserResponse
from app.schemas.restaurant import RestaurantResponse
from app.schemas.delivery import DeliveryPartnerResponse
from app.core.security import validate_password_strength


class CustomerRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    email: EmailStr = Field(..., description="Campus or personal email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    password: str = Field(..., min_length=8, max_length=128, description="Strong account password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")

    @model_validator(mode="after")
    def validate_password_and_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        validate_password_strength(self.password)
        return self


class RestaurantOwnerRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Owner full name")
    email: EmailStr = Field(..., description="Commercial or campus contact email")
    phone_number: str = Field(..., min_length=5, max_length=20, description="Kitchen/manager contact number")
    password: str = Field(..., min_length=8, max_length=128, description="Strong account password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")
    restaurant_name: str = Field(..., min_length=2, max_length=120, description="Commercial name of dining outlet")
    restaurant_address: str = Field(..., min_length=3, max_length=255, description="Physical location or campus hall")
    restaurant_description: Optional[str] = Field(None, max_length=1000, description="Cuisine type and brief summary")

    @model_validator(mode="after")
    def validate_password_and_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        validate_password_strength(self.password)
        return self


class DeliveryPartnerRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Courier full name")
    email: EmailStr = Field(..., description="Campus or courier email address")
    phone_number: str = Field(..., min_length=5, max_length=20, description="Mobile number for dispatch calls")
    password: str = Field(..., min_length=8, max_length=128, description="Strong account password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")
    vehicle_type: VehicleType = Field(default=VehicleType.BICYCLE, description="Courier vehicle mode")

    @model_validator(mode="after")
    def validate_password_and_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        validate_password_strength(self.password)
        return self


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered user email")
    password: str = Field(..., min_length=1, max_length=128, description="Account password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class AuthMeResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    restaurant: Optional[RestaurantResponse] = None
    delivery_profile: Optional[DeliveryPartnerResponse] = None

    class Config:
        from_attributes = True
