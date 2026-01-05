import os
from datetime import datetime
from uuid import uuid4

from pymongo import MongoClient

from .embeddings import embed

env = os.environ


class MongoDBClient(MongoClient):
    def __init__(self):
        uri = env.get("MONGO_URI", "mongodb://localhost:27017")
        db_name = env.get("MONGO_DB", "ragdb")
        super().__init__(uri)
        self.db = self[db_name]
        self.documents = self.db["documents"]
        self.chunks = self.db["chunks"]

    @staticmethod
    def chunk_text(text: str, size=800, overlap=150) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    def create_document(self, doc_id: str, user_id: int, filename: str, bucket: str, processed: bool, text: str) -> None:
        self.documents.insert_one(
            {
                "_id": doc_id,
                "user_id": user_id,
                "filename": filename,
                "bucket": bucket,
                "processed": processed,
                "text": text,
                "created_at": datetime.utcnow(),
            }
        )

    def update_document(self, doc_id: str, data: dict) -> None:
        self.documents.update_one({"_id": doc_id}, {"$set": data})

    def store_chunk(self, text: str, doc_id: str, user_id: int) -> None:
        vector = embed(text)
        self.chunks.insert_one(
            {
                "_id": uuid4().hex,
                "text": text,
                "document_id": doc_id,
                "user_id": user_id,
                "vector": vector,
            }
        )

    def find_chunks_by_user(self, user_id: int, limit=5) -> list[dict]:
        return list(self.chunks.find({"user_id": user_id}).limit(limit))
