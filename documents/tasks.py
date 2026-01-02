
from celery import shared_task
from .models import Document
from rag_engine.weaviate_client import WeaviateClient
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def process_document(self, doc_id):
    doc = Document.objects.get(id=doc_id)
    
    db_client = WeaviateClient()

    text = doc.file.read().decode("utf-8")

    chunks = db_client.chunk_text(text)

    for chunk in chunks:
        db_client.store_chunk(chunk, doc.id, doc.owner.id)

    doc.processed = True
    doc.save()



@shared_task
def add(x, y):
    return x + y