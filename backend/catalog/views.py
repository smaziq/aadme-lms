from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminRole

from .models import Lesson, LessonAsset, Module, Program
from .serializers import (
    AssetCompleteSerializer,
    AssetPresignSerializer,
    LessonAssetSerializer,
    LessonSerializer,
    ModuleSerializer,
    ProgramSerializer,
)
from .storage import StorageService, lesson_asset_key


class AdminPermissionMixin:
    permission_classes = [IsAuthenticated, IsAdminRole]


class AdminProgramListCreate(AdminPermissionMixin, generics.ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class AdminProgramModuleListCreate(AdminPermissionMixin, generics.ListCreateAPIView):
    serializer_class = ModuleSerializer

    def get_queryset(self):
        return Module.objects.filter(program_id=self.kwargs["program_id"])

    def perform_create(self, serializer):
        program = get_object_or_404(Program, pk=self.kwargs["program_id"])
        serializer.save(program=program)


class AdminModuleLessonListCreate(AdminPermissionMixin, generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(module_id=self.kwargs["module_id"])

    def perform_create(self, serializer):
        module = get_object_or_404(Module, pk=self.kwargs["module_id"])
        serializer.save(module=module)


class AdminLessonAssetPresign(AdminPermissionMixin, APIView):
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        serializer = AssetPresignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filename = serializer.validated_data["filename"]
        content_type = serializer.validated_data["content_type"]
        program_id = lesson.module.program_id
        key = lesson_asset_key(program_id, lesson.id, filename)
        upload_url = StorageService().presign_upload(key, content_type)
        return Response({"storage_key": key, "upload_url": upload_url})


class AdminLessonAssetComplete(AdminPermissionMixin, APIView):
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        serializer = AssetCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        storage_key = data["storage_key"]
        program_id = lesson.module.program_id
        expected_prefix = f"lessons/{program_id}/{lesson.id}/"
        if not storage_key.startswith(expected_prefix):
            return Response(
                {"detail": "Storage key does not belong to this lesson."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            StorageService().get_bytes(storage_key)
        except (FileNotFoundError, OSError):
            return Response(
                {"detail": "Storage object not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        asset = LessonAsset.objects.create(
            lesson=lesson,
            storage_key=storage_key,
            filename=data["filename"],
            content_type=data["content_type"],
            size=data["size"],
        )
        return Response(LessonAssetSerializer(asset).data, status=status.HTTP_201_CREATED)


class AdminLessonAssetUpload(AdminPermissionMixin, APIView):
    """Multipart upload: store bytes and create LessonAsset in one request (local/dev UX)."""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        upload = request.FILES.get("file")
        if upload is None:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        program_id = lesson.module.program_id
        filename = upload.name
        content_type = upload.content_type or "application/octet-stream"
        data = upload.read()
        key = lesson_asset_key(program_id, lesson.id, filename)
        StorageService().put_bytes(key, data, content_type)
        asset = LessonAsset.objects.create(
            lesson=lesson,
            storage_key=key,
            filename=filename,
            content_type=content_type,
            size=len(data),
        )
        return Response(LessonAssetSerializer(asset).data, status=status.HTTP_201_CREATED)