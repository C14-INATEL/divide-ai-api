from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
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

    def get_by_id(self, user_id: UUID) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise AppException(status_code=404, detail="Usuário não encontrado")
        return user

    def update(self, user_id: UUID, data: UserUpdate) -> User:
        user = self.get_by_id(user_id)

        if data.name is not None:
            user.name = data.name

        if data.pix_key and self.repo.get_by_pix_key(data.pix_key):
            raise AppException(status_code=400, detail="Chave PIX já cadastrada")

        if data.pix_key_type is not None:
            user.pix_key_type = data.pix_key_type

        return self.repo.update(user)

    def update_password(self, user_id: UUID, data: UserPasswordUpdate) -> User:
        user = self.get_by_id(user_id)

        if not verify_password(data.old_password, user.password):
            raise AppException(status_code=400, detail="Senha antiga incorreta")

        user.password = hash_password(data.new_password)

        return self.repo.update(user)

    def search_users(self, name: Optional[str] = None, limit: int = 50) -> list[User]:
        if name:
            return self.repo.search_by_name(name, limit)
        return self.repo.get_all(limit)