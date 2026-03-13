from enum import Enum

class PixKeyType(str, Enum):
    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    PHONE = "phone"
    RANDOM = "random"