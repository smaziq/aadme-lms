from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import Student
from accounts.serializers import StudentSerializer
from accounts.services import create_and_send_invite
from catalog.models import Batch, Program
from learning.models import Enrollment

User = get_user_model()


class AdminCreateStudentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        user = User(email=email, role=User.Role.STUDENT)
        user.set_unusable_password()
        user.save()
        student = Student.objects.create(
            user=user,
            full_name=validated_data["full_name"],
            phone=validated_data.get("phone", ""),
        )
        create_and_send_invite(user)
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
        return super().create(validated_data)