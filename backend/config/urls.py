"""
URL configuration for Property Management System.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounting.views import AccountingPeriodViewSet, FinancialTransactionViewSet
from audit.views import AuditLogViewSet
from billing.views import InvoiceViewSet, PaymentMethodViewSet, SubscriptionPlanViewSet, SubscriptionViewSet
from core.views import health_check, metrics, readiness_check
from documents.views import DocumentViewSet
from leases.views import LeaseViewSet
from maintenance.views import MaintenanceRequestViewSet
from payments.views import RentPaymentViewSet
from payments.webhooks import stripe_webhook
from properties.views import PropertyImageViewSet, PropertyViewSet
from reports.views import delete_report, generate_report, get_report_templates, list_reports
from tenants.views import TenantViewSet
from users.views import NotificationPreferenceViewSet, NotificationViewSet

# API Documentation will use Django REST framework's browsable API

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
# Billing endpoints
router.register(r"billing/plans", SubscriptionPlanViewSet, basename="subscription-plan")
router.register(r"billing/subscriptions", SubscriptionViewSet, basename="subscription")
router.register(r"billing/payment-methods", PaymentMethodViewSet, basename="payment-method")
router.register(r"billing/invoices", InvoiceViewSet, basename="invoice")
# Notification endpoints
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"notification-preferences", NotificationPreferenceViewSet, basename="notification-preference")
router.register(r"audit", AuditLogViewSet, basename="audit-log")

# Document endpoints
router.register(r"documents", DocumentViewSet, basename="file-document")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
    # Report endpoints
    path("api/reports/generate/", generate_report, name="generate-report"),
    path("api/reports/list/", list_reports, name="list-reports"),
    path("api/reports/templates/", get_report_templates, name="report-templates"),
    path("api/reports/<int:report_id>/delete/", delete_report, name="delete-report"),
    # Templates and generated documents
    path("api/templates/", include("templates.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Health check endpoints
    path("health/", health_check, name="health-check"),
    path("ready/", readiness_check, name="readiness-check"),
    path("metrics/", metrics, name="metrics"),
]
