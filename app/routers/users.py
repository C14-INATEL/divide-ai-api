from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.exceptions import AppException
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserPasswordUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    try:
        return UserService(db).create(data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    try:
        return UserService(db).get_by_id(user_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, data: UserUpdate, db: Session = Depends(get_db)):
    try:
        return UserService(db).update(user_id, data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.patch("/{user_id}/password", response_model=UserResponse)
def update_user_password(user_id: UUID, data: UserPasswordUpdate, db: Session = Depends(get_db)):
    try:
        return UserService(db).update_password(user_id, data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)