from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.enums.pix_key_type import PixKeyType

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    pix_key: Optional[str] = None
    pix_key_type: Optional[PixKeyType] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    pix_key: Optional[str]
    pix_key_type: Optional[PixKeyType]

    model_config = {"from_attributes": True}