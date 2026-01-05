
from celery import shared_task
from rag_engine.mongodb_client import MongoDBClient

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def process_document(self, doc_id, user_id, file_path, bucket="local", filename=None):
    db_client = MongoDBClient()
    with open(file_path, "rb") as file_handle:
        text = file_handle.read().decode("utf-8")
    chunks = db_client.chunk_text(text)
    for chunk in chunks:
        db_client.store_chunk(chunk, doc_id, user_id)
    db_client.update_document(
        doc_id,
        {
            "text": text,
            "processed": True,
            "bucket": bucket,
            "filename": filename or "",
        },
    )
    return {"doc_id": doc_id, "processed": True}

