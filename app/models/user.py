from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.models.enums.pix_key_type import PixKeyType

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.group_member import GroupMember


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    pix_key: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    pix_key_type: Mapped[Optional[PixKeyType]] = mapped_column(Enum(PixKeyType), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    groups: Mapped[list["Group"]] = relationship("Group", back_populates="creator")
    group_memberships: Mapped[list["GroupMember"]] = relationship("GroupMember", back_populates="user")