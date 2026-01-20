# Property Management System — Development-Ready Specification
## Django + React Full-Stack Application

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [Django Backend Setup](#django-backend-setup)
5. [React Frontend Architecture](#react-frontend-architecture)
6. [API Endpoint Specification](#api-endpoint-specification)
7. [Setup & Deployment Guide](#setup--deployment-guide)

---

## Executive Summary

This property management system enables efficient handling of properties, tenants, leases, maintenance requests, rent collection, and financial reporting through a modern full-stack architecture.

**Key Features:**
- Tenant & Property Management
- Lease Lifecycle Tracking
- Maintenance Request Management
- Online Rent Payment Processing
- Financial Accounting & Reporting
- Document Storage & Management
- Owner/Tenant Portals
- Mobile-Responsive Interface

**Tech Stack:**
- **Backend:** Django 4.2+, Django REST Framework (DRF)
- **Frontend:** React 19, TypeScript, Vite
- **Database:** PostgreSQL 14+
- **Authentication:** JWT (JSON Web Tokens)
- **Deployment:** Docker, AWS/DigitalOcean, Nginx

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Admin Dashboard | Tenant Portal | Owner Portal      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (HTTPS)
┌────────────────────────▼────────────────────────────────────┐
│           Django REST Framework Backend                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Authentication (JWT) | Permissions | Rate Limiting  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Views/Serializers | Business Logic | Validators     │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│         PostgreSQL Database                                  │
│  (Properties, Tenants, Leases, Payments, Maintenance)       │
└─────────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Responsibility |
|--------|-----------------|
| **Authentication** | JWT-based user auth, role-based access control (RBAC) |
| **Properties** | Property records, landlord/owner associations |
| **Tenants** | Tenant profiles, contact info, lease associations |
| **Leases** | Lease agreements, terms, renewal tracking |
| **Maintenance** | Maintenance request lifecycle, work orders, vendor management |
| **Payments** | Rent collection, payment tracking, financial transactions |
| **Accounting** | Income/expense tracking, financial reports, owner statements |
| **Documents** | Lease storage, compliance docs, file management |
| **Notifications** | Email alerts, reminders, owner/tenant communications |

---

## Database Schema

### Core Models & Relationships

```sql
-- Users & Authentication
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_type VARCHAR(20) -- 'admin', 'property_manager', 'owner', 'tenant'
);

-- Properties
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES auth_user(id),
    property_name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    property_type VARCHAR(50), -- 'single_family', 'apartment', 'commercial'
    total_units INTEGER DEFAULT 1,
    purchase_price DECIMAL(12, 2),
    purchase_date DATE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(owner_id, address)
);

-- Tenants
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    social_security_number VARCHAR(11), -- encrypted
    emergency_contact_name VARCHAR(150),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Leases
CREATE TABLE leases (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    lease_start_date DATE NOT NULL,
    lease_end_date DATE NOT NULL,
    monthly_rent DECIMAL(10, 2) NOT NULL,
    deposit_amount DECIMAL(10, 2),
    lease_document_url VARCHAR(500),
    status VARCHAR(50), -- 'active', 'pending', 'expired', 'terminated'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rent Payments
CREATE TABLE rent_payments (
    id SERIAL PRIMARY KEY,
    lease_id INTEGER NOT NULL REFERENCES leases(id),
    payment_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50), -- 'credit_card', 'bank_transfer', 'check'
    status VARCHAR(50), -- 'paid', 'pending', 'overdue', 'refunded'
    transaction_id VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance Requests
CREATE TABLE maintenance_requests (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    tenant_id INTEGER REFERENCES tenants(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(50), -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(50), -- 'open', 'assigned', 'in_progress', 'completed', 'closed'
    assigned_vendor_id INTEGER,
    estimated_cost DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    completion_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Financial Transactions
CREATE TABLE financial_transactions (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    transaction_type VARCHAR(50), -- 'income', 'expense'
    category VARCHAR(100), -- 'rent', 'maintenance', 'utilities', 'insurance', etc.
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    lease_id INTEGER REFERENCES leases(id),
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50), -- 'lease', 'compliance', 'inspection', 'other'
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_by INTEGER NOT NULL REFERENCES auth_user(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id),
    action VARCHAR(100),
    model_name VARCHAR(50),
    object_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Django Backend Setup

### 1. Project Structure

```
property_management_system/
├── manage.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   └── tests.py
│   ├── properties/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── tenants/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── leases/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── maintenance/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── payments/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── accounting/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── tests.py
└── core/
    ├── pagination.py
    ├── permissions.py
    ├── exceptions.py
    ├── filters.py
    └── utilities.py
```

### 2. Installation & Dependencies

**requirements.txt:**

```
Django==4.2.8
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-dotenv==1.0.0
psycopg2-binary==2.9.9
djangorestframework-simplejwt==5.3.2
django-filter==23.5
django-extensions==3.2.3
celery==5.3.4
redis==5.0.1
Pillow==10.1.0
requests==2.31.0
stripe==7.3.0
gunicorn==21.2.0
whitenoise==6.6.0
```

### 3. Django Models (Core Examples)

**apps/users/models.py:**

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('manager', 'Property Manager'),
        ('owner', 'Property Owner'),
        ('tenant', 'Tenant'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
```

**apps/properties/models.py:**

```python
from django.db import models
from django.core.validators import MinValueValidator

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = (
        ('single_family', 'Single Family Home'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('commercial', 'Commercial'),
        ('other', 'Other'),
    )
    
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='properties')
    property_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    total_units = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.property_name} - {self.address}"
    
    def get_occupancy_rate(self):
        """Calculate occupancy percentage"""
        from apps.leases.models import Lease
        active_leases = Lease.objects.filter(
            property=self,
            status='active'
        ).count()
        if self.total_units == 0:
            return 0
        return (active_leases / self.total_units) * 100
```

**apps/leases/models.py:**

```python
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Lease(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    )
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='leases')
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lease_document_url = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('property', 'tenant', 'lease_start_date')
        ordering = ['-lease_start_date']
    
    def __str__(self):
        return f"Lease: {self.tenant} - {self.property}"
    
    @property
    def days_remaining(self):
        return (self.lease_end_date - timezone.now().date()).days
    
    @property
    def is_ending_soon(self):
        return 0 <= self.days_remaining <= 30
    
    def save(self, *args, **kwargs):
        if timezone.now().date() > self.lease_end_date:
            self.status = 'expired'
        elif timezone.now().date() >= self.lease_start_date:
            self.status = 'active'
        super().save(*args, **kwargs)
```

### 4. DRF Serializers (Example)

**apps/properties/serializers.py:**

```python
from rest_framework import serializers
from apps.properties.models import Property

class PropertySerializer(serializers.ModelSerializer):
    occupancy_rate = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'owner_name', 'property_name', 'address', 'city',
            'state', 'zip_code', 'property_type', 'total_units', 'purchase_price',
            'purchase_date', 'description', 'is_active', 'occupancy_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'occupancy_rate']
    
    def get_occupancy_rate(self, obj):
        return round(obj.get_occupancy_rate(), 2)
    
    def validate_total_units(self, value):
        if value < 1:
            raise serializers.ValidationError("Total units must be at least 1")
        return value
```

### 5. DRF Views & Viewsets

**apps/properties/views.py:**

```python
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.properties.models import Property
from apps.properties.serializers import PropertySerializer
from core.permissions import IsPropertyOwner

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'is_active', 'city', 'state']
    search_fields = ['property_name', 'address', 'city']
    ordering_fields = ['created_at', 'property_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Property.objects.all()
        return Property.objects.filter(owner=user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def occupancy_details(self, request, pk=None):
        """Get detailed occupancy information for a property"""
        property_obj = self.get_object()
        from apps.leases.models import Lease
        
        active_leases = Lease.objects.filter(
            property=property_obj,
            status='active'
        ).values('id', 'tenant__first_name', 'tenant__last_name', 'monthly_rent')
        
        return Response({
            'total_units': property_obj.total_units,
            'occupied_units': len(active_leases),
            'occupancy_rate': property_obj.get_occupancy_rate(),
            'active_leases': active_leases
        })
```

### 6. URL Configuration

**config/urls.py:**

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import UserViewSet
from apps.properties.views import PropertyViewSet
from apps.tenants.views import TenantViewSet
from apps.leases.views import LeaseViewSet
from apps.maintenance.views import MaintenanceRequestViewSet
from apps.payments.views import RentPaymentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'maintenance', MaintenanceRequestViewSet, basename='maintenance')
router.register(r'payments', RentPaymentViewSet, basename='payment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### 7. Permissions & Authentication

**core/permissions.py:**

```python
from rest_framework import permissions

class IsPropertyOwner(permissions.BasePermission):
    """Only property owner can edit/delete"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsAdminOrOwner(permissions.BasePermission):
    """Admin or object owner"""
    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'admin' or obj.owner == request.user

class IsTenantOrAdmin(permissions.BasePermission):
    """Tenant can only see own data"""
    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'admin' or obj.tenant.user_id == request.user.id
```

**config/settings/base.py:**

```python
from datetime import timedelta

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_extensions',
    
    # Local apps
    'apps.users',
    'apps.properties',
    'apps.tenants',
    'apps.leases',
    'apps.maintenance',
    'apps.payments',
    'apps.accounting',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
]

AUTH_USER_MODEL = 'users.User'
```

---

## React Frontend Architecture

### 1. Project Structure

```
property-management-frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── vite-env.d.ts
│   ├── api/
│   │   ├── client.ts          # Axios instance with interceptors
│   │   ├── endpoints.ts       # API endpoint constants
│   │   └── auth.ts            # Authentication API calls
│   ├── hooks/
│   │   ├── useAuth.ts         # Authentication hook
│   │   ├── useFetch.ts        # Data fetching hook
│   │   ├── useForm.ts         # Form handling hook
│   │   └── useNotification.ts # Toast/notification hook
│   ├── context/
│   │   ├── AuthContext.tsx    # Auth state
│   │   └── NotificationContext.tsx
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Loading.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── PrivateRoute.tsx
│   │   ├── properties/
│   │   │   ├── PropertyList.tsx
│   │   │   ├── PropertyCard.tsx
│   │   │   ├── PropertyDetail.tsx
│   │   │   ├── PropertyForm.tsx
│   │   │   └── PropertyOccupancy.tsx
│   │   ├── tenants/
│   │   │   ├── TenantList.tsx
│   │   │   ├── TenantCard.tsx
│   │   │   ├── TenantDetail.tsx
│   │   │   └── TenantForm.tsx
│   │   ├── leases/
│   │   │   ├── LeaseList.tsx
│   │   │   ├── LeaseDetail.tsx
│   │   │   ├── LeaseForm.tsx
│   │   │   └── RenewalTracker.tsx
│   │   ├── maintenance/
│   │   │   ├── MaintenanceList.tsx
│   │   │   ├── MaintenanceDetail.tsx
│   │   │   ├── MaintenanceForm.tsx
│   │   │   └── RequestStatus.tsx
│   │   ├── payments/
│   │   │   ├── PaymentList.tsx
│   │   │   ├── PaymentForm.tsx
│   │   │   ├── PaymentHistory.tsx
│   │   │   └── RentCollection.tsx
│   │   └── dashboard/
│   │       ├── AdminDashboard.tsx
│   │       ├── TenantDashboard.tsx
│   │       ├── OwnerDashboard.tsx
│   │       ├── MetricsCard.tsx
│   │       └── Charts.tsx
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── PropertiesPage.tsx
│   │   ├── TenantsPage.tsx
│   │   ├── LeasesPage.tsx
│   │   ├── MaintenancePage.tsx
│   │   ├── PaymentsPage.tsx
│   │   ├── AccountingPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── utils/
│   │   ├── formatters.ts      # Date, currency formatting
│   │   ├── validators.ts      # Form validation
│   │   ├── constants.ts       # App constants
│   │   └── helpers.ts         # Utility functions
│   ├── types/
│   │   ├── index.ts           # TypeScript interfaces
│   │   ├── api.ts             # API response types
│   │   └── models.ts          # Domain models
│   └── styles/
│       ├── globals.css
│       ├── variables.css
│       └── components.css
└── public/
    └── assets/
```

### 2. package.json

```json
{
  "name": "property-management-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.5",
    "typescript": "^5.3.3",
    "@tanstack/react-query": "^5.28.0",
    "zustand": "^4.4.7",
    "date-fns": "^2.30.0",
    "recharts": "^2.10.3",
    "classnames": "^2.3.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "eslint": "^8.55.0",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0"
  }
}
```

### 3. API Client Setup

**src/api/client.ts:**

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && originalRequest) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${data.access}`;
          }
          return client(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;
```

**src/api/endpoints.ts:**

```typescript
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/token/',
    REFRESH: '/token/refresh/',
    LOGOUT: '/logout/',
    REGISTER: '/users/',
  },
  
  // Properties
  PROPERTIES: {
    LIST: '/properties/',
    DETAIL: (id: number) => `/properties/${id}/`,
    OCCUPANCY: (id: number) => `/properties/${id}/occupancy_details/`,
    CREATE: '/properties/',
    UPDATE: (id: number) => `/properties/${id}/`,
    DELETE: (id: number) => `/properties/${id}/`,
  },
  
  // Tenants
  TENANTS: {
    LIST: '/tenants/',
    DETAIL: (id: number) => `/tenants/${id}/`,
    CREATE: '/tenants/',
    UPDATE: (id: number) => `/tenants/${id}/`,
    DELETE: (id: number) => `/tenants/${id}/`,
  },
  
  // Leases
  LEASES: {
    LIST: '/leases/',
    DETAIL: (id: number) => `/leases/${id}/`,
    CREATE: '/leases/',
    UPDATE: (id: number) => `/leases/${id}/`,
    DELETE: (id: number) => `/leases/${id}/`,
  },
  
  // Maintenance
  MAINTENANCE: {
    LIST: '/maintenance/',
    DETAIL: (id: number) => `/maintenance/${id}/`,
    CREATE: '/maintenance/',
    UPDATE: (id: number) => `/maintenance/${id}/`,
  },
  
  // Payments
  PAYMENTS: {
    LIST: '/payments/',
    DETAIL: (id: number) => `/payments/${id}/`,
    CREATE: '/payments/',
    UPDATE: (id: number) => `/payments/${id}/`,
  },
};
```

### 4. Custom Hooks

**src/hooks/useAuth.ts:**

```typescript
import { useState, useContext, useCallback } from 'react';
import client from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  email: string;
  first_name: string;
  last_name: string;
  user_type: string;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    user_type: string;
  };
}

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await client.post<AuthResponse>(API_ENDPOINTS.AUTH.LOGIN, credentials);
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      setUser(data.user);
      return data.user;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Login failed';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await client.post(API_ENDPOINTS.AUTH.REGISTER, data);
      // Optionally auto-login after registration
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Registration failed';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

  return { user, loading, error, login, register, logout };
};
```

**src/hooks/useFetch.ts:**

```typescript
import { useState, useEffect, useCallback } from 'react';
import client from '../api/client';

interface UseFetchOptions {
  refetchInterval?: number;
  skip?: boolean;
}

export const useFetch = <T,>(
  url: string,
  options: UseFetchOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!options.skip);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (options.skip) return;
    
    setLoading(true);
    try {
      const response = await client.get<T>(url);
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [url, options.skip]);

  useEffect(() => {
    fetchData();

    if (options.refetchInterval) {
      const interval = setInterval(fetchData, options.refetchInterval);
      return () => clearInterval(interval);
    }
  }, [fetchData, options.refetchInterval]);

  return { data, loading, error, refetch: fetchData };
};
```

### 5. TypeScript Types

**src/types/models.ts:**

```typescript
export interface Property {
  id: number;
  owner: number;
  owner_name: string;
  property_name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: 'single_family' | 'apartment' | 'condo' | 'townhouse' | 'commercial' | 'other';
  total_units: number;
  purchase_price?: number;
  purchase_date?: string;
  description: string;
  is_active: boolean;
  occupancy_rate: number;
  created_at: string;
  updated_at: string;
}

export interface Tenant {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth?: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  created_at: string;
  updated_at: string;
}

export interface Lease {
  id: number;
  property: number;
  tenant: number;
  lease_start_date: string;
  lease_end_date: string;
  monthly_rent: number;
  deposit_amount?: number;
  status: 'pending' | 'active' | 'expired' | 'terminated';
  lease_document_url?: string;
  notes: string;
  days_remaining?: number;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceRequest {
  id: number;
  property: number;
  tenant?: number;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'assigned' | 'in_progress' | 'completed' | 'closed';
  estimated_cost?: number;
  actual_cost?: number;
  completion_date?: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface RentPayment {
  id: number;
  lease: number;
  payment_date: string;
  amount: number;
  payment_method: 'credit_card' | 'bank_transfer' | 'check';
  status: 'paid' | 'pending' | 'overdue' | 'refunded';
  transaction_id?: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'admin' | 'manager' | 'owner' | 'tenant';
  phone_number: string;
  profile_picture?: string;
  created_at: string;
  updated_at: string;
}
```

### 6. React Component Example

**src/components/properties/PropertyList.tsx:**

```typescript
import React, { useState } from 'react';
import { useFetch } from '../../hooks/useFetch';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Property } from '../../types/models';
import PropertyCard from './PropertyCard';
import Button from '../common/Button';
import Loading from '../common/Loading';

const PropertyList: React.FC = () => {
  const [filters, setFilters] = useState({ property_type: '', city: '' });
  const { data, loading, error } = useFetch<{ results: Property[] }>(
    `${API_ENDPOINTS.PROPERTIES.LIST}?property_type=${filters.property_type}`
  );

  if (loading) return <Loading />;
  if (error) return <div className="error">Error loading properties</div>;

  const properties = data?.results || [];

  return (
    <div className="property-list">
      <div className="header">
        <h1>Properties</h1>
        <Button variant="primary">Add Property</Button>
      </div>

      <div className="filters">
        <input
          type="text"
          placeholder="Filter by city"
          value={filters.city}
          onChange={(e) => setFilters({ ...filters, city: e.target.value })}
        />
      </div>

      <div className="grid">
        {properties.map((property) => (
          <PropertyCard key={property.id} property={property} />
        ))}
      </div>
    </div>
  );
};

export default PropertyList;
```

---

## API Endpoint Specification

### Authentication Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/api/token/` | Login (obtain JWT) | None |
| POST | `/api/token/refresh/` | Refresh access token | Bearer Token |
| POST | `/api/users/` | Register new user | None |

### Properties Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/properties/` | List all properties (filtered by owner) | Bearer |
| POST | `/api/properties/` | Create new property | Bearer |
| GET | `/api/properties/{id}/` | Get property details | Bearer |
| PUT | `/api/properties/{id}/` | Update property | Bearer |
| DELETE | `/api/properties/{id}/` | Delete property | Bearer |
| GET | `/api/properties/{id}/occupancy_details/` | Get occupancy info | Bearer |

### Tenants Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/tenants/` | List all tenants | Bearer |
| POST | `/api/tenants/` | Create new tenant | Bearer |
| GET | `/api/tenants/{id}/` | Get tenant details | Bearer |
| PUT | `/api/tenants/{id}/` | Update tenant | Bearer |
| DELETE | `/api/tenants/{id}/` | Delete tenant | Bearer |

### Leases Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/leases/` | List all leases (filterable by status) | Bearer |
| POST | `/api/leases/` | Create new lease | Bearer |
| GET | `/api/leases/{id}/` | Get lease details | Bearer |
| PUT | `/api/leases/{id}/` | Update lease | Bearer |
| DELETE | `/api/leases/{id}/` | Delete lease | Bearer |

### Maintenance Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/maintenance/` | List maintenance requests (filterable by priority, status) | Bearer |
| POST | `/api/maintenance/` | Create maintenance request | Bearer |
| GET | `/api/maintenance/{id}/` | Get request details | Bearer |
| PATCH | `/api/maintenance/{id}/` | Update request status | Bearer |

### Payments Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/payments/` | List payments (filterable by status, date range) | Bearer |
| POST | `/api/payments/` | Record payment | Bearer |
| GET | `/api/payments/{id}/` | Get payment details | Bearer |
| PATCH | `/api/payments/{id}/` | Mark payment as paid | Bearer |

---

## Setup & Deployment Guide

### Local Development Setup

#### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

#### Backend Setup

```bash
# Clone repository
git clone <repo-url>
cd property-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Create database
createdb property_mgmt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata samples.json

# Run development server
python manage.py runserver
# API will be at http://localhost:8000/api/
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd property-management-frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Run development server
npm run dev
# Frontend will be at http://localhost:5173/
```

### Docker Setup

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: property_mgmt
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://user:password@db:5432/property_mgmt
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - .:/code

  frontend:
    build: ./property-management-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://backend:8000/api
    depends_on:
      - backend

volumes:
  postgres_data:
```

```bash
# Run with Docker Compose
docker-compose up

# Access
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin (user/password)
```

### Production Deployment

#### Environment Variables (.env.production)

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/property_mgmt
CORS_ALLOWED_ORIGINS=https://yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
STATIC_URL=/static/
STATIC_ROOT=/home/app/staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=/home/app/media/
```

#### Gunicorn + Nginx

**nginx.conf:**

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    client_max_body_size 10M;

    location /static/ {
        alias /home/app/staticfiles/;
    }

    location /media/ {
        alias /home/app/media/;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri /index.html;
        root /home/app/dist;
    }
}
```

#### Deployment Steps (AWS EC2 Example)

```bash
# Connect to server
ssh -i key.pem ubuntu@your-instance

# Install dependencies
sudo apt update && sudo apt install -y python3-pip postgresql nginx docker.io

# Clone repository
git clone <repo-url> /home/ubuntu/app
cd /home/ubuntu/app

# Set permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/app

# Create .env from .env.example
cp .env.example .env
nano .env  # Edit with production values

# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Run containers
docker-compose -f docker-compose.prod.yml up -d

# Collect static files
docker exec property-mgmt-backend python manage.py collectstatic --noinput

# Verify deployment
curl http://localhost:8000/api/
```

#### CI/CD with GitHub Actions

**.github/workflows/deploy.yml:**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: |
          python -m pip install -r requirements.txt
          python manage.py test
      
      - name: Build and deploy
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          mkdir -p ~/.ssh
          echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh -i ~/.ssh/deploy_key ubuntu@${{ secrets.SERVER_IP }} 'cd /home/ubuntu/app && git pull && docker-compose up -d'
```

---

## Additional Implementation Notes

### Best Practices Implemented

1. **API Security:**
   - JWT authentication with refresh tokens
   - Role-based access control (RBAC)
   - Input validation on both frontend and backend
   - CORS configuration
   - Rate limiting

2. **Performance:**
   - Database query optimization (select_related, prefetch_related)
   - Pagination on list endpoints
   - Frontend lazy loading
   - Caching strategies with Redis ready

3. **Code Quality:**
   - TypeScript for type safety
   - Django models with validators
   - DRF serializer validation
   - Component-based React architecture
   - Environment variable configuration

4. **Testing:**
   - Django TestCase for models and views
   - React component testing with Vitest
   - Integration tests for critical flows

### Next Steps for Development

1. Implement email notifications (rent reminders, maintenance updates)
2. Add payment processing integration (Stripe)
3. Build tenant portal interface
4. Create financial reporting module
5. Implement file upload/document storage
6. Add multi-property analytics dashboard
7. Mobile app (React Native)
8. Automated backup system

---

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Author:** Development Team
