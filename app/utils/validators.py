from typing import Optional


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError('Senha deve ter pelo menos 8 caracteres')
    if not any(char.isupper() for char in password):
        raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
    if not any(char.islower() for char in password):
        raise ValueError('Senha deve conter pelo menos uma letra minúscula')
    if not any(char.isdigit() for char in password):
        raise ValueError('Senha deve conter pelo menos um número')
    return password


def validate_pix_key(pix_key: Optional[str]) -> Optional[str]:
    if pix_key and len(pix_key.strip()) == 0:
        raise ValueError('Chave PIX não pode ser vazia se fornecida')
    return pix_key


def validate_name(name: Optional[str]) -> Optional[str]:
    if name is not None and name.strip() == "":
        raise ValueError('Nome não pode ser vazio')
    return name
