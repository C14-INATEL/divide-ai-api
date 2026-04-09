from uuid import UUID, uuid4
from typing import Optional

from app.models.user import User
from app.models.enums.pix_key_type import PixKeyType


class InMemoryUserRepository:
    
    def __init__(self):
        self._users_by_id: dict[UUID, User] = {}
        self._users_by_email: dict[str, User] = {}
        self._users_by_pix: dict[str, User] = {}
    
    def create(self, email: str, name: str, hashed_password: str, 
               pix_key: Optional[str], pix_key_type: Optional[PixKeyType]) -> User:
        user = User(
            email=email,
            name=name,
            password=hashed_password,
            pix_key=pix_key,
            pix_key_type=pix_key_type,
        )
        user.id = uuid4()
        
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user
        if user.pix_key:
            self._users_by_pix[user.pix_key] = user
        
        return user
    
    def get_by_email(self, email: str) -> User | None:
        return self._users_by_email.get(email)
    
    def get_by_pix_key(self, pix_key: str) -> User | None:
        return self._users_by_pix.get(pix_key)
    
    def get_by_id(self, user_id: UUID) -> User | None:
        return self._users_by_id.get(user_id)
    
    def update(self, user: User) -> User:
        if user.id in self._users_by_id:
            old_user = self._users_by_id[user.id]
            
            if old_user.email in self._users_by_email:
                del self._users_by_email[old_user.email]
            if old_user.pix_key and old_user.pix_key in self._users_by_pix:
                del self._users_by_pix[old_user.pix_key]
        
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user
        if user.pix_key:
            self._users_by_pix[user.pix_key] = user
        
        return user
    
    def search_by_name(self, name: str, limit: int = 50) -> list[User]:
        results = [
            user for user in self._users_by_id.values()
            if name.lower() in user.name.lower()
        ]
        return results[:limit]
    
    def get_all(self, limit: int = 50) -> list[User]:
        return list(self._users_by_id.values())[:limit]
    
    def add_user(self, user: User) -> None:
        if not user.id:
            user.id = uuid4()
        
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user
        if user.pix_key:
            self._users_by_pix[user.pix_key] = user
