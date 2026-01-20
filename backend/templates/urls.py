from django.urls import path

from .views import (
    list_templates, get_template, get_template_variables,
    generate_document, list_generated_documents, download_document, validate_template
)

urlpatterns = [
    path('', list_templates, name='list-templates'),
    path('list/', list_templates, name='list-templates-alt'),  # Keep for backward compatibility
    path('<int:template_id>/', get_template, name='get-template'),
    path('<int:template_id>/variables/', get_template_variables, name='template-variables'),
    path('generate/', generate_document, name='generate-document'),
    path('generated/', list_generated_documents, name='list-generated-documents'),
    path('generated/<int:document_id>/download/', download_document, name='download-document'),
    path('validate/', validate_template, name='validate-template'),
]