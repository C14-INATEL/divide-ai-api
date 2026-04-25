import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.validators.group_validators import validate_group_name, validate_group_name_required


class GroupCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_group_name_required(v)


class GroupUpdate(BaseModel):
    name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return validate_group_name(v)


class UserInGroupOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class GroupMemberDetail(BaseModel):
    user_id: uuid.UUID
    joined_at: datetime
    user: UserInGroupOut

    model_config = ConfigDict(from_attributes=True)


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: list[GroupMemberDetail] = []

    model_config = ConfigDict(from_attributes=True)


class GroupMemberAdd(BaseModel):
    user_id: uuid.UUID


class GroupMemberOut(BaseModel):
    user_id: uuid.UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
