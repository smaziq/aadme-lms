from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import InviteToken, Student

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


class SetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            invite = InviteToken.objects.select_related("user").get(token=attrs["token"])
        except InviteToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or expired invite token"})
        if invite.used_at is not None:
            raise serializers.ValidationError({"token": "This invite has already been used"})
        if invite.expires_at < timezone.now():
            raise serializers.ValidationError({"token": "This invite has expired"})
        attrs["invite"] = invite
        return attrs

    def save(self, **kwargs):
        invite = self.validated_data["invite"]
        user = invite.user
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])
        invite.mark_used()
        token, _ = Token.objects.get_or_create(user=user)
        return {"token": token.key, "user": user}