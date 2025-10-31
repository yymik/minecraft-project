from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .dialogflow import get_dialogflow_response


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)
    session_id = serializers.CharField(max_length=64, required=False, allow_blank=True)


class ChatbotMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        session_id = serializer.validated_data.get("session_id") or (
            str(request.user.pk) if request.user.is_authenticated else request.session.session_key or "guest"
        )
        reply = get_dialogflow_response(message, session_id=session_id)
        return Response({"reply": reply}, status=status.HTTP_200_OK)
