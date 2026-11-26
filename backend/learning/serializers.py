from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers

from accounts.models import Student
from accounts.serializers import StudentSerializer
from accounts.services import create_and_send_invite
from catalog.models import Batch, Lesson, LessonAsset, Module, Program
from learning.models import Enrollment, LessonCompletion

User = get_user_model()


class AdminCreateStudentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def create(self, validated_data):
        email = validated_data["email"]
        with transaction.atomic():
            user = User(email=email, role=User.Role.STUDENT)
            user.set_unusable_password()
            user.save()
            student = Student.objects.create(
                user=user,
                full_name=validated_data["full_name"],
                phone=validated_data.get("phone", ""),
            )
            transaction.on_commit(lambda: create_and_send_invite(user))
        return student

    def to_representation(self, instance):
        return StudentSerializer(instance).data


class AdminEnrollmentCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="student"
    )
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), source="program"
    )
    batch_id = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(), source="batch", required=False, allow_null=True
    )

    class Meta:
        model = Enrollment
        fields = ("id", "student_id", "program_id", "batch_id", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")

    def validate(self, attrs):
        student = attrs["student"]
        program = attrs["program"]
        batch = attrs.get("batch")
        if batch is not None and batch.program_id != program.id:
            raise serializers.ValidationError({"batch_id": "Batch does not belong to this program."})
        if Enrollment.objects.filter(
            student=student, program=program, status=Enrollment.Status.ACTIVE
        ).exists():
            raise serializers.ValidationError("Active enrollment already exists for this student and program.")
        return attrs

    def create(self, validated_data):
        validated_data.setdefault("status", Enrollment.Status.ACTIVE)
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                "Active enrollment already exists for this student and program."
            )


class AdminEnrollmentListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    student_email = serializers.EmailField(source="student.user.email", read_only=True)
    program_title = serializers.CharField(source="program.title", read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "student_id",
            "student_name",
            "student_email",
            "program_id",
            "program_title",
            "status",
            "created_at",
            "progress",
        )

    def get_progress(self, enrollment):
        return progress_for_student_program(enrollment.student, enrollment.program_id)


def progress_for_student_program(student, program_id: int) -> dict:
    published_lessons = Lesson.objects.filter(module__program_id=program_id, is_published=True)
    total = published_lessons.count()
    completed = LessonCompletion.objects.filter(
        student=student, lesson__in=published_lessons
    ).count()
    percent = round((completed / total) * 100, 2) if total else 0
    return {"completed": completed, "total": total, "percent": percent}


class StudentProgramSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("id", "title", "slug", "description")


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    program = StudentProgramSummarySerializer(read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ("id", "status", "created_at", "program", "progress")

    def get_progress(self, enrollment):
        return progress_for_student_program(enrollment.student, enrollment.program_id)


class StudentLessonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "order")


class StudentModuleTreeSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ("id", "title", "order", "lessons")

    def get_lessons(self, module):
        lessons = module.lessons.filter(is_published=True)
        return StudentLessonSummarySerializer(lessons, many=True).data


class StudentProgramTreeSerializer(serializers.ModelSerializer):
    modules = StudentModuleTreeSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = ("id", "title", "slug", "description", "modules")


class StudentLessonAssetSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()
    playback_url = serializers.SerializerMethodField()
    playback_expires_at = serializers.SerializerMethodField()

    PLAYBACK_EXPIRES_IN = 900

    class Meta:
        model = LessonAsset
        fields = (
            "id",
            "filename",
            "content_type",
            "size",
            "download_url",
            "kind",
            "delivery",
            "playback_url",
            "playback_expires_at",
        )

    def _playback(self, asset):
        """Return (url, expires_at_iso_or_None) for video assets; cached per instance."""
        from datetime import timedelta

        from django.conf import settings
        from django.utils import timezone

        from catalog.storage import StorageService, is_video_content_type

        cache = self.context.setdefault("_playback_cache", {})
        if asset.id in cache:
            return cache[asset.id]
        if not is_video_content_type(asset.content_type):
            cache[asset.id] = (None, None)
            return cache[asset.id]
        if settings.LMS_USE_LOCAL_STORAGE:
            result = (f"/api/me/assets/{asset.id}/stream/", None)
        else:
            url = StorageService().presign_download(
                asset.storage_key, expires_in=self.PLAYBACK_EXPIRES_IN
            )
            expires = timezone.now() + timedelta(seconds=self.PLAYBACK_EXPIRES_IN)
            result = (url, expires.isoformat())
        cache[asset.id] = result
        return result

    def get_download_url(self, asset):
        return f"/api/me/assets/{asset.id}/download/"

    def get_kind(self, asset):
        from catalog.storage import is_video_content_type

        return "video" if is_video_content_type(asset.content_type) else "file"

    def get_delivery(self, asset):
        from django.conf import settings

        from catalog.storage import is_video_content_type

        if not is_video_content_type(asset.content_type):
            return "download"
        if settings.LMS_USE_LOCAL_STORAGE:
            return "mp4_proxy"
        return "mp4_signed"

    def get_playback_url(self, asset):
        return self._playback(asset)[0]

    def get_playback_expires_at(self, asset):
        return self._playback(asset)[1]


class StudentLessonDetailSerializer(serializers.ModelSerializer):
    assets = StudentLessonAssetSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ("id", "title", "order", "body", "links", "assets", "is_completed")

    def get_is_completed(self, lesson):
        student = self.context.get("student")
        if student is None:
            return False
        return LessonCompletion.objects.filter(student=student, lesson=lesson).exists()


class LessonCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompletion
        fields = ("id", "lesson", "completed_at")
        read_only_fields = fields