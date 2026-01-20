"""
URL configuration for Property Management System.

The `urlpatterns` list routes URLs to views.
"""

from accounting.views import AccountingPeriodViewSet, FinancialTransactionViewSet
from core.views import health_check, readiness_check, metrics
from documents.views import DocumentViewSet
from django.contrib import admin
from django.urls import include, path
from leases.views import LeaseViewSet
from maintenance.views import MaintenanceRequestViewSet
from payments.views import RentPaymentViewSet
from properties.views import PropertyImageViewSet, PropertyViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from tenants.views import TenantViewSet
from payments.webhooks import stripe_webhook

# Global error handlers
handler404 = "core.exceptions.handler404"
handler500 = "core.exceptions.handler500"

# Import ViewSets
from users.views import UserViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"property-images", PropertyImageViewSet, basename="property-image")
router.register(r"tenants", TenantViewSet, basename="tenant")
router.register(r"leases", LeaseViewSet, basename="lease")
router.register(r"maintenance", MaintenanceRequestViewSet, basename="maintenance")
router.register(r"payments", RentPaymentViewSet, basename="payment")
router.register(r"accounting/transactions", FinancialTransactionViewSet, basename="transaction")
router.register(r"accounting/periods", AccountingPeriodViewSet, basename="accounting-period")
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
    # Health check endpoints
    path("health/", health_check, name="health-check"),
    path("ready/", readiness_check, name="readiness-check"),
    path("metrics/", metrics, name="metrics"),
]
