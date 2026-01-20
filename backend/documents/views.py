from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing file documents"""

    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter documents based on query parameters"""
        queryset = Document.objects.filter(uploaded_by=self.request.user)

        # Filter by model type
        model_name = self.request.query_params.get('model_name')
        if model_name:
            try:
                content_type = ContentType.objects.get(
                    app_label='properties',  # Adjust based on your app structure
                    model=model_name
                )
                queryset = queryset.filter(
                    content_type=content_type,
                    object_id=self.request.query_params.get('object_id')
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()

        return queryset

    def perform_create(self, serializer):
        """Set the uploaded_by field when creating a document"""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download a document file"""
        try:
            document = self.get_object()

            # Check if user has permission to access this document
            if document.uploaded_by != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if not document.file:
                return Response(
                    {'error': 'File not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Return file response
            from django.http import FileResponse
            response = FileResponse(document.file.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{document.file.name.split("/")[-1]}"'
            return response

        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Download failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )