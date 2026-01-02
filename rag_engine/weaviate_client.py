import weaviate
import os
from .embeddings import embed

env = os.environ


schema = {
    "class": "Chunk",
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "document_id", "dataType": ["int"]},
        {"name": "user_id", "dataType": ["int"]},
    ],
    "vectorizer": "none",
}


class WeaviateClient:
    def __init__(self):
        self.client = weaviate.Client(
            url=env["WEAVIATE_URL"],
        )

        if not self.client.schema.exists("Chunk"):
            self.client.schema.create_class(schema)

    def chunk_text(text: str, size=800, overlap=150, is_embed=False) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
    
    def store_chunk(self, text: str, doc_id: int, user_id: int):
        
        vector = embed(text)

        self.client.data_object.create(
            {
                "text": text,
                "document_id": doc_id,
                "user_id": user_id
            },
            "Chunk",
            vector=vector
        )