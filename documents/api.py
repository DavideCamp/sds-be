from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .tasks import process_document

class UploadDocument(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        f = request.FILES["file"]

        doc = Document.objects.create(
            owner=request.user,
            file=f,
            filename=f.name
        )

        process_document.delay(doc.id)

        return Response({"document_id": doc.id, "status": "queued"})
