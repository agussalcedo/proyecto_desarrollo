"""
Services - Business Logic Layer
"""
from typing import Optional, List
from passlib.context import CryptContext

from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.repository.get_by_email(email)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.repository.get_all(skip, limit)

    def create_user(self, user_data: UserCreate) -> User:
        if self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")
        if self.repository.get_by_username(user_data.username):
            raise ValueError("Username already taken")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=self._hash_password(user_data.password),
        )
        return self.repository.create(user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        return self.repository.update(user)

    def delete_user(self, user_id: int) -> bool:
        user = self.repository.get_by_id(user_id)
        if not user:
            return False
        self.repository.delete(user)
        return True

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.repository.get_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        return user
