from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""

    content_type_name = serializers.CharField(source="content_type.name", read_only=True)
    changed_fields = serializers.SerializerMethodField()
    is_sensitive = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "username",
            "user",
            "content_type",
            "content_type_name",
            "object_id",
            "action",
            "action_description",
            "old_values",
            "new_values",
            "changed_fields",
            "ip_address",
            "user_agent",
            "timestamp",
            "app_label",
            "model_name",
            "is_sensitive",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_changed_fields(self, obj):
        return obj.changed_fields

    def get_is_sensitive(self, obj):
        return obj.is_sensitive_action
