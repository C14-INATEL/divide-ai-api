from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator
from app.models.enums.pix_key_type import PixKeyType

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    pix_key: Optional[str] = None
    pix_key_type: Optional[PixKeyType] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not any(char.isupper() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not any(char.islower() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('Senha deve conter pelo menos um número')
        return v

    @field_validator('pix_key')
    @classmethod
    def validate_pix_key(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Chave PIX não pode ser vazia se fornecida')
        return v

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    pix_key: Optional[str]
    pix_key_type: Optional[PixKeyType]

    model_config = {"from_attributes": True}