"""
URL configuration for Property Management System.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import ViewSets
from users.views import UserViewSet
from properties.views import PropertyViewSet, PropertyImageViewSet
from tenants.views import TenantViewSet
from leases.views import LeaseViewSet
from maintenance.views import MaintenanceRequestViewSet
from payments.views import RentPaymentViewSet
from accounting.views import FinancialTransactionViewSet, AccountingPeriodViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'property-images', PropertyImageViewSet, basename='property-image')
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'maintenance', MaintenanceRequestViewSet, basename='maintenance')
router.register(r'payments', RentPaymentViewSet, basename='payment')
router.register(r'accounting/transactions', FinancialTransactionViewSet, basename='transaction')
router.register(r'accounting/periods', AccountingPeriodViewSet, basename='accounting-period')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
