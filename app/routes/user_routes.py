from typing import List
from fastapi import APIRouter, HTTPException, status
from app.core.database import database
from app.schemas.user_schema import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    repo = UserRepository(database)
    service = UserService(repo)
    try:
        return await service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Esto ayuda a ver errores no controlados en la terminal
        print(f"Internal Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100):
    repo = UserRepository(database)
    service = UserService(repo)
    return await service.get_all_users(skip, limit)