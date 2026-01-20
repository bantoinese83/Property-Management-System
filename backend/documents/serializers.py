from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for file documents"""

    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)
    content_type_name = serializers.CharField(source="content_type.name", read_only=True)
    model_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "file",
            "file_name",
            "file_type",
            "file_size",
            "content_type",
            "content_type_name",
            "object_id",
            "model_name",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "file_name", "file_size", "file_type", "content_type", "uploaded_by", "created_at", "updated_at"]

    def validate_file(self, value):
        """Validate uploaded file for security and size constraints"""
        if not value:
            raise serializers.ValidationError("File is required")

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")

        # Check file type by content
        allowed_mime_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'image/jpeg',
            'image/png',
            'image/gif',
        ]

        if hasattr(value, 'content_type') and value.content_type not in allowed_mime_types:
            raise serializers.ValidationError(
                f"File type '{value.content_type}' is not allowed. "
                "Allowed types: PDF, Word documents, Excel spreadsheets, text files, and images (JPEG, PNG, GIF)."
            )

        # Additional security: check file extension matches content type
        file_name = value.name.lower()
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.jar', '.php', '.asp', '.js']
        for ext in dangerous_extensions:
            if file_name.endswith(ext):
                raise serializers.ValidationError(f"File type '{ext}' is not allowed for security reasons")

        return value

    def validate_title(self, value):
        """Validate document title"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required and cannot be empty")
        if len(value) > 255:
            raise serializers.ValidationError("Title cannot exceed 255 characters")
        return value.strip()

    def create(self, validated_data):
        # Handle model_name to content_type conversion
        model_name = validated_data.pop("model_name", None)
        if model_name:
            try:
                content_type = ContentType.objects.get(
                    app_label="properties", model=model_name.lower()
                )
                validated_data["content_type"] = content_type
            except ContentType.DoesNotExist:
                raise serializers.ValidationError({"model_name": "Invalid model name"})

        # Handle file upload with enhanced validation
        file = validated_data.get("file")
        if file:
            validated_data["file_size"] = file.size
            # Extract file type from uploaded file
            file_name = file.name.lower()
            if file_name.endswith((".pdf",)):
                validated_data["file_type"] = "pdf"
            elif file_name.endswith((".doc", ".docx")):
                validated_data["file_type"] = "doc" if file_name.endswith(".doc") else "docx"
            elif file_name.endswith((".xls", ".xlsx")):
                validated_data["file_type"] = "xls" if file_name.endswith(".xls") else "xlsx"
            elif file_name.endswith((".txt",)):
                validated_data["file_type"] = "txt"
            elif file_name.endswith((".jpg", ".jpeg", ".png", ".gif")):
                validated_data["file_type"] = file_name.split(".")[-1]
            else:
                validated_data["file_type"] = "other"

        return super().create(validated_data)
