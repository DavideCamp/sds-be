import os
from datetime import datetime, timezone
from uuid import uuid4, UUID

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.collections.classes.filters import Filter

from .embeddings import embed

env = os.environ


class WeaviateClient:
    def __init__(self):
        self.chunks_index = env.get("WEAVIATE_INDEX", "chunks")
        self.documents_index = env.get("WEAVIATE_DOCUMENTS_INDEX", "documents")
        self.text_key = env.get("WEAVIATE_TEXT_KEY", "text")
        self.client = weaviate.connect_to_local(skip_init_checks=True)
        self._ensure_schema()
        self.chunks_collection = self.client.collections.get(self.chunks_index)
        self.documents_collection = self.client.collections.get(self.documents_index)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()

    def _ensure_schema(self) -> None:
        if not self.client.collections.exists(self.chunks_index):
            self.client.collections.create(
                name=self.chunks_index,
                vector_config=Configure.Vectors.self_provided(),
                properties=[
                    Property(name=self.text_key, data_type=DataType.TEXT),
                    Property(name="object_id", data_type=DataType.TEXT, index_filterable=True),
                    Property(name="document_id", data_type=DataType.TEXT, index_filterable=True),
                    Property(name="user_id", data_type=DataType.INT, index_filterable=True),
                ],
            )

        if not self.client.collections.exists(self.documents_index):
            self.client.collections.create(
                name=self.documents_index,
                vector_config=Configure.Vectors.self_provided(),
                properties=[
                    Property(name=self.text_key, data_type=DataType.TEXT),
                    Property(name="object_id", data_type=DataType.TEXT, index_filterable=True),
                    Property(name="document_id", data_type=DataType.TEXT, index_filterable=True),
                    Property(name="user_id", data_type=DataType.INT, index_filterable=True),
                    Property(name="filename", data_type=DataType.TEXT),
                    Property(name="bucket", data_type=DataType.TEXT),
                    Property(name="processed", data_type=DataType.BOOL),
                    Property(name="created_at", data_type=DataType.DATE),
                    Property(name="doc_type", data_type=DataType.TEXT),
                ],
            )

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
        properties = {
            self.text_key: text,
            "object_id": doc_id,
            "document_id": doc_id,
            "user_id": user_id,
            "filename": filename,
            "bucket": bucket,
            "processed": processed,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "doc_type": "source",
        }
        vector = embed(text) if text else None
        self.documents_collection.data.insert(
            properties=properties,
            uuid=doc_id,
            vector=vector,
        )


    def update_document(self, doc_id: str, data: dict) -> None:
        try:
            # Convert string to UUID object
            uuid_obj = UUID(doc_id)
            existing = self.documents_collection.query.fetch_object_by_id(uuid_obj)
            if existing is None:
                print(f"Document {doc_id} not found")
                return
            self.documents_collection.data.update(uuid=uuid_obj, properties=data)
            print(f"Successfully updated document {doc_id}")
        except ValueError as e:
            print(f"Invalid UUID format: {doc_id}, error: {e}")
        except Exception as e:
            print(f"Error updating document {doc_id}: {e}")

    def store_chunk(self, text: str, doc_id: str, user_id: int) -> None:
        chunk_id = str(uuid4())
        self.chunks_collection.data.insert(
            properties={
                self.text_key: text,
                "object_id": chunk_id,
                "document_id": doc_id,
                "user_id": user_id,
            },
            uuid=chunk_id,
            vector=embed(text),
        )

    def similarity_search(self, query: str, user_id: int, limit: int = 5) -> list[dict]:
        filters = Filter.by_property("user_id").equal(user_id)
        response = self.chunks_collection.query.near_vector(
            near_vector=embed(query),
            limit=limit,
            filters=filters,
            return_metadata=["distance"],
            return_properties=[self.text_key, "document_id", "user_id", "object_id"],
        )
        formatted = []
        for obj in response.objects:
            props = obj.properties or {}
            formatted.append(
                {
                    "_id": props.get("object_id"),
                    "text": props.get(self.text_key),
                    "document_id": props.get("document_id"),
                    "user_id": props.get("user_id"),
                    "score": obj.metadata.distance if obj.metadata else None,
                }
            )
        return formatted

    def find_chunks_by_user(self, user_id: int, limit: int = 5) -> list[dict]:
        filters = Filter.by_property("user_id").equal(user_id)
        response = self.chunks_collection.query.fetch_objects(
            limit=limit,
            filters=filters,
            return_properties=[self.text_key, "document_id", "user_id", "object_id"],
        )
        items = response.objects
        results = []
        for item in items:
            props = item.properties or {}
            results.append(
                {
                    "_id": props.get("object_id"),
                    "text": props.get(self.text_key),
                    "document_id": props.get("document_id"),
                    "user_id": props.get("user_id"),
                }
            )
        return results