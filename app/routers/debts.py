import uuid
from fastapi import APIRouter, Depends, Response, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse, DebtListResponse, DebtParticipantOut
from app.services.debt_service import DebtService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/debts", tags=["debts"])


@router.post("/", response_model=DebtResponse, status_code=201)
def create_debt(
    data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).create(data, creator_id=current_user.id)


@router.get("/", response_model=list[DebtListResponse])
def list_debts(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).list_by_group(group_id, current_user_id=current_user.id)


@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(
    debt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).get_by_id(debt_id, current_user_id=current_user.id)


@router.patch("/{debt_id}", response_model=DebtResponse)
def update_debt(
    debt_id: uuid.UUID,
    data: DebtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).update(debt_id, data, current_user_id=current_user.id)


@router.delete("/{debt_id}", status_code=204)
def delete_debt(
    debt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    DebtService(db).delete(debt_id, current_user_id=current_user.id)
    return Response(status_code=204)


@router.post(
    "/{debt_id}/participants/me/proof",
    response_model=DebtParticipantOut,
    status_code=201,
)
def upload_proof(
    debt_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).upload_proof(
        debt_id=debt_id,
        current_user_id=current_user.id,
        file=file,
    )


@router.post(
    "/{debt_id}/participants/{user_id}/confirm",
    response_model=DebtParticipantOut,
)
def confirm_payment(
    debt_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).confirm_payment(
        debt_id=debt_id,
        participant_user_id=user_id,
        current_user_id=current_user.id,
    )


@router.get("/{debt_id}/participants/{user_id}/proof")
def get_proof(
    debt_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DebtService(db).get_proof(
        debt_id=debt_id,
        participant_user_id=user_id,
        current_user_id=current_user.id,
    )
