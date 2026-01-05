from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import DocumentUploadSerializer

class UploadDocument(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return Response({"detail": "Missing 'files'."}, status=status.HTTP_400_BAD_REQUEST)
        document_ids = []
        for file in files:
            serializer = DocumentUploadSerializer(data={"file": file}, context={"request": request})
            serializer.is_valid(raise_exception=True)
            doc = serializer.save()
            document_ids.append(doc["id"])

        return Response(
            {"status": "success", "document_ids": document_ids},
            status=status.HTTP_201_CREATED
        )
