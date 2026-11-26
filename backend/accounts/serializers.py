from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Student

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("id", "full_name", "phone", "crm_person_id")


class UserSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "role", "student")

    def get_student(self, obj):
        profile = getattr(obj, "student_profile", None)
        if profile is None:
            return None
        return StudentSerializer(profile).data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            user = authenticate(
                username=attrs["email"],
                password=attrs["password"],
            )
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials")
        attrs["user"] = user
        return attrs