from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DocumentTemplate, GeneratedDocument
from .services import TemplateService
from .serializers import DocumentTemplateSerializer, GeneratedDocumentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """List available document templates"""
    try:
        templates = DocumentTemplate.objects.filter(is_active=True)

        # Filter by category if provided
        category = request.query_params.get('category')
        if category:
            templates = templates.filter(category=category)

        # Filter by type if provided
        template_type = request.query_params.get('type')
        if template_type:
            templates = templates.filter(template_type=template_type)

        serializer = DocumentTemplateSerializer(templates, many=True)
        return Response({'templates': serializer.data})

    except Exception as e:
        return Response(
            {'error': f'Failed to list templates: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template(request, template_id):
    """Get a specific template with variable information"""
    try:
        template = DocumentTemplate.objects.get(id=template_id, is_active=True)

        serializer = DocumentTemplateSerializer(template)
        variables_info = TemplateService.get_template_variables(template)

        return Response({
            'template': serializer.data,
            'variables': variables_info
        })

    except DocumentTemplate.DoesNotExist:
        return Response(
            {'error': 'Template not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get template: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template_variables(request, template_id):
    """Get template variables information"""
    try:
        template = DocumentTemplate.objects.get(id=template_id, is_active=True)
        variables_info = TemplateService.get_template_variables(template)
        return Response({'variables': variables_info})

    except DocumentTemplate.DoesNotExist:
        return Response(
            {'error': 'Template not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get template variables: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_document(request):
    """Generate a document from a template"""
    try:
        template_id = request.data.get('template_id')
        variables = request.data.get('variables', {})
        title = request.data.get('title', 'Generated Document')
        related_model = request.data.get('related_model')
        related_id = request.data.get('related_id')

        if not template_id:
            return Response(
                {'error': 'template_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = TemplateService.generate_document(
            template_id=int(template_id),
            variables=variables,
            title=title,
            user=request.user,
            related_model=related_model,
            related_id=int(related_id) if related_id else None
        )

        serializer = GeneratedDocumentSerializer(document)
        return Response({
            'document': serializer.data,
            'message': 'Document generated successfully'
        })

    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to generate document: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_generated_documents(request):
    """List user's generated documents"""
    try:
        documents = GeneratedDocument.objects.filter(created_by=request.user)

        # Filter by status if provided
        doc_status = request.query_params.get('status')
        if doc_status:
            documents = documents.filter(status=doc_status)

        # Filter by template type if provided
        template_type = request.query_params.get('template_type')
        if template_type:
            documents = documents.filter(template__template_type=template_type)

        serializer = GeneratedDocumentSerializer(documents[:50], many=True)  # Limit to 50
        return Response({'documents': serializer.data})

    except Exception as e:
        return Response(
            {'error': f'Failed to list documents: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_document(request, document_id):
    """Download a generated document"""
    try:
        document = GeneratedDocument.objects.get(
            id=document_id,
            created_by=request.user,
            status__in=['generated', 'sent', 'signed']
        )

        if not document.generated_content:
            return Response(
                {'error': 'Document content not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Return the document content as a downloadable file
        from django.http import HttpResponse
        response = HttpResponse(document.generated_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{document.title}.txt"'
        return response

    except GeneratedDocument.DoesNotExist:
        return Response(
            {'error': 'Document not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to download document: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_template(request):
    """Validate template content"""
    try:
        content = request.data.get('content', '')

        if not content:
            return Response(
                {'error': 'Template content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        validation_result = TemplateService.validate_template(content)

        return Response({
            'validation': validation_result,
            'is_valid': validation_result['is_valid']
        })

    except Exception as e:
        return Response(
            {'error': f'Validation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )