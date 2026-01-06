from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message
from chat.rag import rag_answer
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data["question"]


        answer = rag_answer(question, request.user)


        return Response({"answer": answer})
