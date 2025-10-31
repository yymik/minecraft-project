from datetime import datetime

from django.db import DatabaseError
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WikiPage
from .opennamu_client import get_opennamu_client
from .views import wiki  # reuse existing Mongo client


class WikiSummarySerializer(serializers.Serializer):
    title = serializers.CharField()
    summary = serializers.CharField()
    updated_at = serializers.DateTimeField(required=False)
    tags = serializers.CharField(required=False)


class WikiContentSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()
    summary = serializers.CharField(required=False, allow_blank=True)


class WikiListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        pages = []
        try:
            for page in WikiPage.objects.all()[:100]:
                pages.append(
                    {
                        "title": page.title,
                        "summary": page.summary or page.content[:120],
                        "updated_at": page.updated_at,
                        "tags": page.tags,
                    }
                )
        except DatabaseError:
            pass

        if not pages:
            try:
                cursor = wiki.find({}, {"title": 1, "content": 1, "updated_at": 1}).limit(100)
                for doc in cursor:
                    pages.append(
                        {
                            "title": doc.get("title", ""),
                            "summary": (doc.get("content") or "")[:120],
                            "updated_at": doc.get("updated_at"),
                        }
                    )
            except (PyMongoError, ServerSelectionTimeoutError):
                pages = []

        serializer = WikiSummarySerializer(pages, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class WikiDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, title):
        opennamu = get_opennamu_client()
        if opennamu.enabled:
            remote = opennamu.fetch_page(title)
            if remote:
                return Response(
                    {
                        "title": remote.get("title", title),
                        "content": remote.get("content", ""),
                        "summary": remote.get("summary", ""),
                        "source": "opennamu",
                    },
                    status=status.HTTP_200_OK,
                )

        try:
            page = WikiPage.objects.filter(title=title).first()
        except DatabaseError:
            page = None

        if page:
            serializer = WikiContentSerializer(
                {
                    "title": page.title,
                    "content": page.content,
                    "summary": page.summary,
                }
            )
            return Response({**serializer.data, "source": "django"}, status=status.HTTP_200_OK)

        doc = None
        try:
            doc = wiki.find_one({"title": title})
        except (PyMongoError, ServerSelectionTimeoutError):
            doc = None

        if doc:
            serializer = WikiContentSerializer(
                {
                    "title": doc.get("title", title),
                    "content": doc.get("content", ""),
                    "summary": doc.get("summary", ""),
                }
            )
            return Response({**serializer.data, "source": "mongo"}, status=status.HTTP_200_OK)

        return Response({"detail": "문서를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, title):
        self.check_object_permissions(request, title)
        serializer = WikiContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        opennamu = get_opennamu_client()
        if opennamu.enabled:
            success = opennamu.push_page(title, data["content"], data.get("summary", ""))
            if not success:
                return Response({"detail": "openNAMU 저장에 실패했습니다."}, status=status.HTTP_502_BAD_GATEWAY)
            return Response({"detail": "openNAMU 문서를 저장했습니다."}, status=status.HTTP_200_OK)

        try:
            page, created = WikiPage.objects.get_or_create(title=title, defaults={"content": data["content"]})
            page.content = data["content"]
            if data.get("summary"):
                page.summary = data["summary"]
            page.save(update_fields=["content", "summary", "updated_at"])
            source = "created" if created else "updated"
            return Response({"detail": f"Django 위키 문서를 {source}했습니다."}, status=status.HTTP_200_OK)
        except DatabaseError:
            pass

        try:
            wiki.update_one(
                {"title": title},
                {
                    "$set": {
                        "content": data["content"],
                        "summary": data.get("summary", ""),
                        "updated_at": datetime.utcnow(),
                    }
                },
                upsert=True,
            )
            return Response({"detail": "MongoDB 문서를 저장했습니다."}, status=status.HTTP_200_OK)
        except (PyMongoError, ServerSelectionTimeoutError):
            return Response({"detail": "문서를 저장하지 못했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
