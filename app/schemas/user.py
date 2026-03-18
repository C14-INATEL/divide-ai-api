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
    if v is None:
        return v

    if len(v.strip()) == 0:
        raise ValueError('Chave PIX não pode ser vazia se fornecida')

    pix_patterns = [
        (r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$',                          'CPF'),
        (r'^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$',                   'CNPJ'),
        (r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',     'E-mail'),
        (r'^(\+55)?\d{2}9?\d{8}$',                                    'Telefone'),
        (r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', 'UUID'),
    ]

    if not any(re.match(pattern, v.strip()) for pattern, _ in pix_patterns):
        raise ValueError(
            'Chave PIX inválida. Formatos aceitos: '
            'CPF, CNPJ, e-mail, telefone ou chave aleatória (UUID)'
        )

    return v.strip()

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    pix_key: Optional[str]
    pix_key_type: Optional[PixKeyType]

    model_config = {"from_attributes": True}