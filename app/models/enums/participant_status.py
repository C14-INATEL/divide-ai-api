from enum import Enum


class ParticipantStatus(str, Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    CONFIRMADO = "confirmado"
