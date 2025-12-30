
from celery import shared_task
from .models import Document

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def process_document(self, doc_id):
    doc = Document.objects.get(id=doc_id)

    # placeholder – qui andrà OCR + chunking
    import time
    time.sleep(5)

    doc.processed = True
    doc.save()
