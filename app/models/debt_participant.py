import uuid
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Numeric, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.debt import Debt
    from app.models.user import User


class DebtParticipant(Base):
    __tablename__ = "debt_participants"

    debt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("debts.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pendente")
    has_proof: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    proof_path: Mapped[str] = mapped_column(String, nullable=True)
    paid_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    debt: Mapped["Debt"] = relationship("Debt", back_populates="participants")
    user: Mapped["User"] = relationship("User")
