import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums.debt_split_type import DebtSplitType
from app.models.enums.participant_status import ParticipantStatus
from app.schemas.group import UserInGroupOut


class DebtParticipantInput(BaseModel):
    user_id: uuid.UUID
    percentage: Optional[Decimal] = None


class DebtCreate(BaseModel):
    group_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    total_amount: Decimal
    split_type: DebtSplitType
    participants: list[DebtParticipantInput] = []


class DebtUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    total_amount: Optional[Decimal] = None
    split_type: Optional[DebtSplitType] = None
    participants: Optional[list[DebtParticipantInput]] = None


class DebtParticipantOut(BaseModel):
    user_id: uuid.UUID
    user: UserInGroupOut
    percentage: Decimal
    amount: Decimal
    status: ParticipantStatus
    has_proof: bool
    paid_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DebtResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    total_amount: Decimal
    split_type: DebtSplitType
    status: str
    created_at: datetime
    updated_at: datetime
    participants: list[DebtParticipantOut] = []

    model_config = ConfigDict(from_attributes=True)


class DebtSummary(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    total_amount: Decimal
    split_type: DebtSplitType
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DebtListResponse(DebtSummary):
    participants: list[DebtParticipantOut] = []

    model_config = ConfigDict(from_attributes=True)
