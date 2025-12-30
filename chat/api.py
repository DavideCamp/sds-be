from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message
from .rag import rag_answer

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        question = request.data["message"]

        session = ChatSession.objects.get(id=session_id, user=request.user)
        Message.objects.create(session=session, role="user", content=question)

        answer = rag_answer(question, request.user)

        Message.objects.create(session=session, role="assistant", content=answer)

        return Response({"answer": answer})
