from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.get_collection("users")

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        document = await self.collection.find_one({"_id": ObjectId(user_id)})
        if document:
            document["id"] = str(document.pop("_id"))
        return document

    async def get_by_email(self, email: str) -> Optional[dict]:
        document = await self.collection.find_one({"email": email})
        if document:
            document["id"] = str(document.pop("_id"))
        return document

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        for doc in await cursor.to_list(length=limit):
            doc["id"] = str(doc.pop("_id"))
            users.append(doc)
        return users

    async def create(self, user_data: dict) -> dict:
        result = await self.collection.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        if "_id" in user_data:
            del user_data["_id"]
        return user_data

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0