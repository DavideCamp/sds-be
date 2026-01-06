
from celery import shared_task
from rag_engine.weaviate_client import WeaviateClient



@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def process_document(self, doc_id, user_id, file_path, bucket="local", filename=None):
    import logging
    logger = logging.getLogger(__name__)

    with WeaviateClient() as client:

        logger.info(f"Processing document {doc_id}")

        with open(file_path, "rb") as file_handle:
            text = file_handle.read().decode("utf-8")
        chunks = client.chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks for document {doc_id}")

        for chunk in chunks:
            client.store_chunk(chunk, doc_id, user_id)


        # Log before update
        logger.info(f"Updating document {doc_id} to processed=True")
        client.update_document(
                    doc_id,
                    {
                        "text": text,
                        "processed": True,
                        "bucket": bucket,
                        "filename": filename or "",
                    },
                )
        logger.info(f"Update result for {doc_id}")

    return {"doc_id": doc_id, "processed": True}