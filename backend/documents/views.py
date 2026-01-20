from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        content_type = self.request.query_params.get("content_type")
        model_name = self.request.query_params.get("model_name")
        object_id = self.request.query_params.get("object_id")
        
        if model_name and object_id:
            from django.contrib.contenttypes.models import ContentType
            mapping = {
                "property": ("properties", "property"),
                "tenant": ("tenants", "tenant"),
                "lease": ("leases", "lease"),
                "maintenance": ("maintenance", "maintenancerequest"),
                "payment": ("payments", "rentpayment"),
            }
            if model_name.lower() in mapping:
                app_label, model = mapping[model_name.lower()]
                queryset = queryset.filter(content_type__app_label=app_label, content_type__model=model, object_id=object_id)
            else:
                queryset = queryset.filter(content_type__model=model_name.lower(), object_id=object_id)
        elif content_type and object_id:
            queryset = queryset.filter(content_type=content_type, object_id=object_id)
            
        return queryset
