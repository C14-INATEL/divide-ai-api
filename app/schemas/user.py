from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator
from app.models.enums.pix_key_type import PixKeyType
from app.utils.validators import validate_password_strength, validate_pix_key, validate_name

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    pix_key: Optional[str] = None
    pix_key_type: Optional[PixKeyType] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

    @field_validator('pix_key')
    @classmethod
    def validate_pix(cls, v):
        return validate_pix_key(v)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    pix_key: Optional[str] = None
    pix_key_type: Optional[PixKeyType] = None

    @field_validator('name')
    @classmethod
    def validate_user_name(cls, v):
        return validate_name(v)

    @field_validator('pix_key')
    @classmethod
    def validate_pix(cls, v):
        return validate_pix_key(v)

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        return validate_password_strength(v)

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    pix_key: Optional[str]
    pix_key_type: Optional[PixKeyType]

    model_config = {"from_attributes": True}