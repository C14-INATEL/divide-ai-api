from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password
from app.models.user import User
from app.exceptions import AppException

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise AppException(status_code=400, detail="Email já cadastrado")

        if data.pix_key and self.repo.get_by_pix_key(data.pix_key):
            raise AppException(status_code=400, detail="Chave PIX já cadastrada")

        return self.repo.create(
            email=data.email,
            name=data.name,
            hashed_password=hash_password(data.password),
            pix_key=data.pix_key,
            pix_key_type=data.pix_key_type,
        )

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            return None
        return user