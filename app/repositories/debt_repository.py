import uuid
import os
from sqlalchemy.orm import Session, selectinload
from app.models.debt import Debt
from app.models.debt_participant import DebtParticipant
from app.models.group_member import GroupMember


class DebtRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, debt: Debt) -> Debt:
        self.db.add(debt)
        self.db.flush()
        self.db.refresh(debt)
        return debt

    def list_by_group(self, group_id: uuid.UUID) -> list[Debt]:
        return (
            self.db.query(Debt)
            .options(selectinload(Debt.participants).selectinload(DebtParticipant.user))
            .filter(Debt.group_id == group_id)
            .all()
        )

    def get_by_id(self, debt_id: uuid.UUID) -> Debt | None:
        return (
            self.db.query(Debt)
            .options(selectinload(Debt.participants).selectinload(DebtParticipant.user))
            .filter(Debt.id == debt_id)
            .first()
        )

    def delete(self, debt: Debt) -> None:
        self.db.delete(debt)
        self.db.commit()

    def get_participant(self, debt_id: uuid.UUID, user_id: uuid.UUID) -> DebtParticipant | None:
        return (
            self.db.query(DebtParticipant)
            .filter(DebtParticipant.debt_id == debt_id, DebtParticipant.user_id == user_id)
            .first()
        )

    def update_participant(self, participant: DebtParticipant) -> DebtParticipant:
        self.db.commit()
        self.db.refresh(participant)
        return participant
