from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, name: str, hashed_password: str, pix_key: str, pix_key_type) -> User:
        user = User(
            email=email,
            name=name,
            password=hashed_password,
            pix_key=pix_key,
            pix_key_type=pix_key_type,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()