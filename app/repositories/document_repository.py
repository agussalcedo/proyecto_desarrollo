"""
Document Repository - Data Access Layer (MongoDB)
"""
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class DocumentRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        # Cambiamos la colección de "users" a "documents"
        self.collection = database.get_collection("documents")

    async def get_by_id(self, doc_id: str) -> Optional[dict]:
        document = await self.collection.find_one({"_id": ObjectId(doc_id)})
        if document:
            document["id"] = str(document.pop("_id"))
        return document

    async def get_by_checksum(self, checksum: str) -> Optional[dict]:
        """
        Busca un documento por su suma de verificación.
        Crucial para cumplir con el requisito de no duplicados.
        """
        document = await self.collection.find_one({"checksum": checksum})
        if document:
            document["id"] = str(document.pop("_id"))
        return document

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        documents = []
        for doc in await cursor.to_list(length=limit):
            doc["id"] = str(doc.pop("_id"))
            documents.append(doc)
        return documents

    async def create(self, doc_data: dict) -> dict:
        """
        Persiste el contenido y el checksum en la base de datos.
        """
        result = await self.collection.insert_one(doc_data)
        doc_data["id"] = str(result.inserted_id)
        if "_id" in doc_data:
            del doc_data["_id"]
        return doc_data

    async def update(self, doc_id: str, update_data: dict) -> Optional[dict]:
        """
        Actualiza un documento persistido (Parte del CRUD solicitado).
        """
        await self.collection.update_one(
            {"_id": ObjectId(doc_id)}, 
            {"$set": update_data}
        )
        return await self.get_by_id(doc_id)

    async def delete(self, doc_id: str) -> bool:
        """
        Elimina un documento de la base de datos.
        """
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0