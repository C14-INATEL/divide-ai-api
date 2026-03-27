from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.services.user_service import UserService
from app.utils.api_errors import raise_error_response, GenericBadRequest
from app.utils.jwt import create_access_token

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = UserService(db).authenticate(data.email, data.password)
    if not user:
        return raise_error_response(GenericBadRequest({"description": "Credenciais inválidas"}))
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return LoginResponse(access_token=token)
