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
    rules = [
        (r'.{8,}',           'Senha deve ter pelo menos 8 caracteres'),
        (r'[A-Z]',           'Senha deve conter pelo menos uma letra maiúscula'),
        (r'[a-z]',           'Senha deve conter pelo menos uma letra minúscula'),
        (r'\d',              'Senha deve conter pelo menos um número'),
    ]

    for pattern, message in rules:
        if not re.search(pattern, v):
            raise ValueError(message)

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