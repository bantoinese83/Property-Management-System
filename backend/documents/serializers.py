from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for file documents"""

    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)
    content_type_name = serializers.CharField(source="content_type.name", read_only=True)

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
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "file_name", "file_size", "uploaded_by", "created_at", "updated_at"]

    def create(self, validated_data):
        # Handle file upload
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
