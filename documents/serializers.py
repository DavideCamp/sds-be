from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from documents.tasks import process_document
from rag_engine.weviate_client import WeaviateClient


DEFAULT_ALLOWED_MIME_TYPES = getattr(
    settings,
    "DOCUMENT_ALLOWED_MIME_TYPES",
    ("text/plain", "text/markdown", "text/csv", "application/json"),
)
DEFAULT_MAX_UPLOAD_SIZE = getattr(settings, "DOCUMENT_MAX_UPLOAD_SIZE", 25 * 1024 * 1024)
DEFAULT_STORAGE_SUBDIR = getattr(settings, "DOCUMENT_STORAGE_SUBDIR", "documents")
DEFAULT_STORAGE_BUCKET = getattr(settings, "DOCUMENT_STORAGE_BUCKET", "local")


class DocumentUploadSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    file = serializers.FileField(required=True, write_only=True)
    filename = serializers.CharField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    processed = serializers.BooleanField(read_only=True)

    def validate_file(self, value):
        if value.size == 0:
            raise serializers.ValidationError("Empty file uploads are not allowed.")
        if value.size > DEFAULT_MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("File exceeds maximum upload size.")
        content_type = (value.content_type or "").lower()
        if DEFAULT_ALLOWED_MIME_TYPES and content_type not in DEFAULT_ALLOWED_MIME_TYPES:
            # Keep in sync with celery task expecting UTF-8 text.
            raise serializers.ValidationError("Unsupported file type.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authenticated user required.")

        upload = validated_data["file"]
        storage_root = Path(settings.MEDIA_ROOT) / DEFAULT_STORAGE_SUBDIR
        storage_root.mkdir(parents=True, exist_ok=True)
        storage = FileSystemStorage(location=storage_root)
        stored_name = f"{uuid4().hex}_{upload.name}"
        saved_name = storage.save(stored_name, upload)
        file_path = storage.path(saved_name)

        document_id = str(uuid4())
        with WeaviateClient() as client:

            client.create_document(
                doc_id=document_id,
                user_id=request.user.id,
                filename=upload.name,
                bucket=DEFAULT_STORAGE_BUCKET,
                processed=False,
                text="",
            )

        process_document.delay(
            doc_id=document_id,
            user_id=request.user.id,
            file_path=file_path,
            bucket=DEFAULT_STORAGE_BUCKET,
            filename=upload.name,
        )

        return {
            "id": document_id,
            "filename": upload.name,
            "uploaded_at": timezone.now(),
            "processed": False,
        }
