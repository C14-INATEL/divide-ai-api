import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.schemas.debt import DebtCreate


class DebtService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DebtCreate, creator_id: uuid.UUID):
        pass

    def list_by_group(self, group_id: uuid.UUID, current_user_id: uuid.UUID):
        pass

    def get_by_id(self, debt_id: uuid.UUID, current_user_id: uuid.UUID):
        pass

    def delete(self, debt_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        pass

    def upload_proof(
        self,
        debt_id: uuid.UUID,
        current_user_id: uuid.UUID,
        file: UploadFile,
    ):
        pass

    def confirm_payment(
        self,
        debt_id: uuid.UUID,
        participant_user_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ):
        pass

    def get_proof(
        self,
        debt_id: uuid.UUID,
        participant_user_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ):
        pass
