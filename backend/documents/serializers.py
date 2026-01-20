from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source="uploaded_by.get_full_name")
    model_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "file",
            "file_type",
            "file_size",
            "content_type",
            "object_id",
            "model_name",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uploaded_by", "file_type", "file_size", "created_at", "updated_at"]
        extra_kwargs = {
            "content_type": {"required": False},
        }

    def validate(self, data):
        model_name = data.get("model_name")
        content_type = data.get("content_type")

        if not content_type and not model_name:
            raise serializers.ValidationError("Either content_type or model_name is required.")

        if model_name:
            try:
                # Map common names to actual app_label.model
                mapping = {
                    "property": ("properties", "property"),
                    "tenant": ("tenants", "tenant"),
                    "lease": ("leases", "lease"),
                    "maintenance": ("maintenance", "maintenancerequest"),
                    "payment": ("payments", "rentpayment"),
                }
                
                if model_name.lower() in mapping:
                    app_label, model = mapping[model_name.lower()]
                    data["content_type"] = ContentType.objects.get(app_label=app_label, model=model)
                else:
                    # Try direct lookup
                    data["content_type"] = ContentType.objects.get(model=model_name.lower())
            except ContentType.DoesNotExist:
                raise serializers.ValidationError({"model_name": f"Invalid model_name: {model_name}"})

        return data

    def create(self, validated_data):
        validated_data.pop("model_name", None)
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)
