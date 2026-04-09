from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.models.enums.pix_key_type import PixKeyType
from typing import Optional
from uuid import UUID

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, name: str, hashed_password: str, pix_key: Optional[str], pix_key_type: Optional[PixKeyType]) -> User:
        user = User(
            email=email,
            name=name,
            password=hashed_password,
            pix_key=pix_key,
            pix_key_type=pix_key_type,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_pix_key(self, pix_key: str) -> User | None:
        return self.db.query(User).filter(User.pix_key == pix_key).first()

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def search_by_name(self, name: str, limit: int = 50) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.name.ilike(f"%{name}%"))
            .limit(limit)
            .all()
        )

    def get_all(self, limit: int = 50) -> list[User]:
        return self.db.query(User).limit(limit).all()