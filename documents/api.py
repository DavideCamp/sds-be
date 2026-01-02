from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .tasks import process_document
from django.db import transaction

class UploadDocument(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        f = request.FILES.get("files")
        if not f:
            return Response({"detail": "Missing 'files'."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            doc = Document.objects.create(
                owner=request.user,
                file=f,
                filename=f.name
            )

            # Enqueue SOLO dopo che il commit è avvenuto
            transaction.on_commit(lambda: process_document.delay(doc.id))

        return Response(
            {"status": "success", "document_id": doc.id},
            status=status.HTTP_201_CREATED
        )