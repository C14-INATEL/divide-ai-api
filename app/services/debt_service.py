import uuid
import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.schemas.debt import DebtCreate
from app.repositories.group_repository import GroupRepository
from app.repositories.user_repository import UserRepository
from app.repositories.debt_repository import DebtRepository
from app.models.debt import Debt
from app.models.debt_participant import DebtParticipant
from app.models.enums.participant_status import ParticipantStatus
from app.models.enums.debt_split_type import DebtSplitType
from app.exceptions import AppException


class DebtService:
    def __init__(self, db: Session):
        self.db = db
        self.group_repo = GroupRepository(db)
        self.user_repo = UserRepository(db)
        self.debt_repo = DebtRepository(db)

    def _assert_member(self, group_id: uuid.UUID, user_id: uuid.UUID):
        member = self.group_repo.get_member(group_id, user_id)
        if not member:
            raise AppException(403, "user is not a member of the group")

    def create(self, data: DebtCreate, creator_id: uuid.UUID):
        group = self.group_repo.get_by_id(data.group_id)
        if not group:
            raise AppException(404, "group not found")

        # creator must be member
        self._assert_member(data.group_id, creator_id)

        total = Decimal(data.total_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        participants_input = data.participants or []
        # if no participants provided, use all group members
        if len(participants_input) == 0:
            # include all members of the group except the creator
            participants_input = []
            for member in group.members:
                if member.user.id == creator_id:
                    continue
                participants_input.append(type("P", (), {"user_id": member.user.id, "percentage": None})())
        n = len(participants_input)
        if n == 0:
            raise AppException(422, "must have at least one participant")

        percentages: list[Decimal] = []
        if data.split_type == DebtSplitType.HOMOGENEA:
            # compute base percentage and distribute rounding remainder to the first participant
            base = (Decimal("100") / Decimal(n))
            per = base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            percentages = [per for _ in range(n)]
            sum_pct = sum(percentages)
            diff_pct = (Decimal("100.00") - sum_pct).quantize(Decimal("0.01"))
            if diff_pct != Decimal("0.00"):
                percentages[0] = (percentages[0] + diff_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            # HETEROGENEA: require percentage for each participant
            for p in participants_input:
                if p.percentage is None:
                    raise AppException(422, "all participants must have percentage for heterogenea split")
                percentages.append(Decimal(p.percentage).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        # verify participants are group members
        for p in participants_input:
            member = self.group_repo.get_member(data.group_id, p.user_id)
            if not member:
                raise AppException(422, f"user {p.user_id} is not a member of the group")

        # verify percentages sum to 100
        total_pct = sum(percentages)
        if total_pct != Decimal("100.00"):
            raise AppException(422, "percentages must sum to 100")

        # compute amounts
        amounts: list[Decimal] = []
        for pct in percentages:
            amt = (total * (pct / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            amounts.append(amt)

        # adjust rounding difference
        sum_amounts = sum(amounts)
        diff = total - sum_amounts
        if diff != Decimal("0.00"):
            amounts[0] = (amounts[0] + diff).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # create debt and participants
        debt = Debt(
            group_id=data.group_id,
            creator_id=creator_id,
            title=data.title,
            description=data.description,
            total_amount=total,
            split_type=data.split_type.value if isinstance(data.split_type, DebtSplitType) else str(data.split_type),
            due_date=data.due_date,
            status="pendente",
        )

        part_objs: list[DebtParticipant] = []
        for inp, pct, amt in zip(participants_input, percentages, amounts):
            part = DebtParticipant(
                user_id=inp.user_id,
                percentage=pct,
                amount=amt,
                status=ParticipantStatus.PENDENTE.value,
                has_proof=False,
            )
            part_objs.append(part)

        debt.participants = part_objs

        self.debt_repo.insert(debt)
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def list_by_group(self, group_id: uuid.UUID, current_user_id: uuid.UUID):
        # ensure user is member
        self._assert_member(group_id, current_user_id)
        return self.debt_repo.list_by_group(group_id)

    def get_by_id(self, debt_id: uuid.UUID, current_user_id: uuid.UUID):
        debt = self.debt_repo.get_by_id(debt_id)
        if not debt:
            raise AppException(404, "debt not found")
        self._assert_member(debt.group_id, current_user_id)
        return debt

    def delete(self, debt_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        debt = self.debt_repo.get_by_id(debt_id)
        if not debt:
            raise AppException(404, "debt not found")
        if debt.creator_id != current_user_id:
            raise AppException(403, "only creator can delete the debt")
        if debt.participants and len(debt.participants) > 0:
            raise AppException(422, "cannot delete debt with participants associated")
        self.debt_repo.delete(debt)

    def upload_proof(
        self,
        debt_id: uuid.UUID,
        current_user_id: uuid.UUID,
        file: UploadFile,
    ):
        debt = self.debt_repo.get_by_id(debt_id)
        if not debt:
            raise AppException(404, "debt not found")
        # participant must be member of the debt
        participant = self.debt_repo.get_participant(debt_id, current_user_id)
        if not participant:
            raise AppException(403, "user is not a participant of the debt")

        # validate file type
        allowed = {"image/jpeg", "image/png", "application/pdf"}
        content_type = getattr(file, "content_type", None)
        if content_type not in allowed:
            raise AppException(422, "file type not allowed; accepted: JPG, PNG, PDF")

        # save file
        upload_dir = os.path.join("uploads", "debts", str(debt_id))
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{current_user_id}_{file.filename}"
        path = os.path.join(upload_dir, filename)
        with open(path, "wb") as f:
            content = file.file.read()
            f.write(content)

        participant.proof_path = path
        participant.has_proof = True
        participant.paid_at = datetime.utcnow()
        participant.status = ParticipantStatus.PAGO.value

        self.debt_repo.update_participant(participant)
        return participant

    def confirm_payment(
        self,
        debt_id: uuid.UUID,
        participant_user_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ):
        debt = self.debt_repo.get_by_id(debt_id)
        if not debt:
            raise AppException(404, "debt not found")
        # only creator can confirm
        if debt.creator_id != current_user_id:
            raise AppException(403, "only creator can confirm payments")
        participant = self.debt_repo.get_participant(debt_id, participant_user_id)
        if not participant:
            raise AppException(404, "participant not found")
        if participant.status != ParticipantStatus.PAGO.value:
            raise AppException(422, "participant has not uploaded proof")
        participant.status = ParticipantStatus.CONFIRMADO.value
        participant.confirmed_at = datetime.utcnow()
        self.debt_repo.update_participant(participant)
        # if all participants are confirmed, mark debt as paid
        all_parts = [p for p in debt.participants]
        if all((p.status == ParticipantStatus.CONFIRMADO.value) for p in all_parts):
            debt.status = "pago"
            self.db.commit()
            self.db.refresh(debt)
        return participant

    def get_proof(
        self,
        debt_id: uuid.UUID,
        participant_user_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ):
        debt = self.debt_repo.get_by_id(debt_id)
        if not debt:
            raise AppException(404, "debt not found")
        # requester must be group member
        self._assert_member(debt.group_id, current_user_id)
        participant = self.debt_repo.get_participant(debt_id, participant_user_id)
        if not participant or not participant.proof_path:
            raise AppException(404, "proof not found")
        if not os.path.exists(participant.proof_path):
            raise AppException(404, "proof not found on disk")
        return FileResponse(participant.proof_path, filename=os.path.basename(participant.proof_path))

