"""
AI URLs for TenantBase
URL patterns for AI-powered features.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'results', views.AIProcessingResultViewSet)
router.register(r'lease-analysis', views.LeaseAnalysisViewSet)
router.register(r'application-analysis', views.TenantApplicationAnalysisViewSet)
router.register(r'maintenance-analysis', views.MaintenanceAnalysisViewSet)
router.register(r'service', views.AIServiceViewSet, basename='ai-service')

urlpatterns = [
    path('', include(router.urls)),
]