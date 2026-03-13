from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.models.enums.pix_key_type import PixKeyType

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