from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserProfile

User = get_user_model()


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        profile = getattr(user, "profile", None)
        token["username"] = user.get_username()
        token["email"] = user.email or ""
        token["minecraft_uuid"] = getattr(profile, "minecraft_uuid", "")
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "username": self.user.get_username(),
            "email": self.user.email or "",
            "minecraft_uuid": getattr(getattr(self.user, "profile", None), "minecraft_uuid", "")
        }
        return data


class AuthTokenView(TokenObtainPairView):
    serializer_class = AuthTokenSerializer


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    minecraft_uuid = serializers.CharField(max_length=36)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("이미 사용 중인 아이디입니다."))
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("이미 사용 중인 이메일입니다."))
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": _("비밀번호가 일치하지 않습니다.")})
        uuid = attrs.get("minecraft_uuid", "").replace("-", "").strip()
        if not uuid:
            raise serializers.ValidationError({"minecraft_uuid": _("Minecraft UUID가 필요합니다.")})
        attrs["normalized_uuid"] = uuid
        if UserProfile.objects.filter(minecraft_uuid__in=[attrs["minecraft_uuid"], uuid]).exists():
            raise serializers.ValidationError({"minecraft_uuid": _("이미 사용 중인 Minecraft UUID입니다.")})
        return attrs


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                is_active=True
            )
            UserProfile.objects.create(user=user, minecraft_uuid=data["normalized_uuid"])

        return Response({"detail": _("회원가입이 완료되었습니다. 로그인해주세요.")}, status=status.HTTP_201_CREATED)
