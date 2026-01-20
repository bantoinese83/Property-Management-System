from rest_framework import serializers

from .models import DocumentTemplate, GeneratedDocument


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for document templates"""

    usage_count = serializers.ReadOnlyField()
    last_used = serializers.ReadOnlyField()

    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'display_name', 'description', 'template_type',
            'category', 'content', 'variables', 'is_active', 'is_system_template',
            'usage_count', 'last_used', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count', 'last_used']


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for generated documents"""

    template_name = serializers.CharField(source='template.display_name', read_only=True)
    template_type = serializers.CharField(source='template.template_type', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = GeneratedDocument
        fields = [
            'id', 'title', 'template', 'template_name', 'template_type',
            'content', 'variables_data', 'generated_content', 'status',
            'recipient_emails', 'sent_at', 'related_model', 'related_id',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'template_name', 'template_type', 'created_by_name']