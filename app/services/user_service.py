from typing import Optional, List
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user(self, user_id: str):
        return await self.repository.get_by_id(user_id)

    async def get_all_users(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip, limit)

    async def create_user(self, user_data: UserCreate):
        if await self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        user_dict = user_data.model_dump()
        # Mapeo de campos para coincidir con UserResponse
        user_dict["is_active"] = True
        
        return await self.repository.create(user_dict)