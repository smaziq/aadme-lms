from rest_framework import serializers

from .models import Lesson, LessonAsset, Module, Program


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "title", "slug", "description", "is_published", "created_at"]
        read_only_fields = ["id", "created_at"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "program", "title", "order"]
        read_only_fields = ["id", "program"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "module", "title", "order", "body", "links", "is_published"]
        read_only_fields = ["id", "module"]


class LessonAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAsset
        fields = ["id", "lesson", "storage_key", "filename", "content_type", "size", "created_at"]
        read_only_fields = fields


class AssetPresignSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=127)


class AssetCompleteSerializer(serializers.Serializer):
    storage_key = serializers.CharField(max_length=512)
    filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=127)
    size = serializers.IntegerField(min_value=0)