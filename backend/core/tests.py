"""
Core test utilities and base test classes for the Property Management System.

This module provides reusable test utilities, fixtures, and base classes
that can be used across all Django apps for consistent testing.
"""

import json
from typing import Any, Dict, List, Optional, Type

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from properties.models import Property
from tenants.models import Tenant
from users.models import User

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common utilities."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = APIClient()

    def tearDown(self):
        """Clean up after tests."""
        super().tearDown()

    def create_user(
        self,
        username: str = "testuser",
        email: str = "test@example.com",
        user_type: str = "owner",
        password: str = "testpass123"
    ) -> User:
        """Create a test user."""
        return User.objects.create_user(
            username=username,
            email=email,
            user_type=user_type,
            password=password,
            first_name="Test",
            last_name="User"
        )

    def authenticate_user(self, user: User) -> None:
        """Authenticate the test client with a user."""
        self.client.force_authenticate(user=user)


class APITestCase(BaseTestCase, APITestCase):
    """Base API test case with authentication and utilities."""

    def setUp(self):
        """Set up API test environment."""
        super().setUp()
        self.user = self.create_user()
        self.authenticate_user(self.user)

    def get_token(self, username: str = "testuser", password: str = "testpass123") -> str:
        """Get authentication token."""
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"]

    def api_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Make an authenticated API request."""
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            kwargs.setdefault("format", "json")

        return getattr(self.client, method.lower())(url, data, **kwargs)


class PropertyTestMixin:
    """Mixin for tests that need property-related objects."""

    def create_property(
        self,
        owner: Optional[User] = None,
        property_name: str = "Test Property",
        **kwargs
    ) -> Property:
        """Create a test property."""
        if owner is None:
            owner = self.user if hasattr(self, 'user') else self.create_user()

        defaults = {
            "property_name": property_name,
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "apartment",
            "total_units": 5,
        }
        defaults.update(kwargs)

        return Property.objects.create(owner=owner, **defaults)

    def create_tenant(
        self,
        first_name: str = "John",
        last_name: str = "Doe",
        email: str = "tenant@example.com",
        **kwargs
    ) -> Tenant:
        """Create a test tenant."""
        defaults = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": "555-0123",
        }
        defaults.update(kwargs)

        return Tenant.objects.create(**defaults)


class IntegrationTestCase(PropertyTestMixin, APITestCase, TransactionTestCase):
    """
    Integration test case for full workflow testing.

    Uses TransactionTestCase for database isolation and provides
    comprehensive test utilities for integration scenarios.
    """

    def setUp(self):
        """Set up integration test environment."""
        super().setUp()
        # Create demo data for integration tests
        call_command("create_demo_data", verbosity=0)

    def test_full_property_workflow(self):
        """Test complete property management workflow."""
        # Create property
        property_data = {
            "property_name": "Integration Test Property",
            "address": "456 Integration Ave",
            "city": "Test City",
            "state": "TC",
            "zip_code": "67890",
            "property_type": "single_family",
            "total_units": 1,
        }

        response = self.api_request("post", reverse("property-list"), property_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        property_id = response.data["id"]

        # Verify property was created
        response = self.api_request("get", reverse("property-detail", args=[property_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["property_name"], "Integration Test Property")

        # Create tenant
        tenant_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "555-0456",
        }

        response = self.api_request("post", reverse("tenant-list"), tenant_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tenant_id = response.data["id"]

        # Create lease
        lease_data = {
            "property_obj": property_id,
            "tenant": tenant_id,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2024-12-31",
            "monthly_rent": 1500.00,
            "deposit_amount": 1500.00,
        }

        response = self.api_request("post", reverse("lease-list"), lease_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify dashboard stats are updated
        response = self.api_request("get", reverse("property-dashboard-stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_properties"], 1)

    def test_payment_workflow(self):
        """Test complete payment processing workflow."""
        # Setup: Create property, tenant, and lease
        property_obj = self.create_property()
        tenant = self.create_tenant()

        lease_data = {
            "property_obj": property_obj.id,
            "tenant": tenant.id,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2024-12-31",
            "monthly_rent": 1200.00,
            "deposit_amount": 1200.00,
        }

        response = self.api_request("post", reverse("lease-list"), lease_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        lease_id = response.data["id"]

        # Create payment
        payment_data = {
            "lease_obj": lease_id,
            "amount": 1200.00,
            "payment_date": "2024-01-01",
            "due_date": "2024-01-01",
            "payment_method": "check",
        }

        response = self.api_request("post", reverse("rentpayment-list"), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify payment was recorded
        response = self.api_request("get", reverse("rentpayment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)


class PerformanceTestCase(BaseTestCase):
    """Base test case for performance testing."""

    def setUp(self):
        """Set up performance test environment."""
        super().setUp()
        # Create bulk test data for performance testing
        self._create_bulk_test_data()

    def _create_bulk_test_data(self, num_properties: int = 50, num_tenants: int = 100):
        """Create bulk test data for performance testing."""
        from leases.models import Lease

        # Create owner
        owner = self.create_user("perf_owner", "perf@example.com")

        # Create properties
        properties = []
        for i in range(num_properties):
            properties.append(self.create_property(
                owner=owner,
                property_name=f"Performance Property {i}",
                address=f"{i} Perf St",
                total_units=5
            ))

        # Create tenants
        tenants = []
        for i in range(num_tenants):
            tenants.append(self.create_tenant(
                first_name=f"Tenant{i}",
                last_name="Perf",
                email=f"tenant{i}@perf.com"
            ))

        # Create leases (linking tenants to properties)
        import random
        for i, tenant in enumerate(tenants[:num_properties]):  # One lease per property
            Lease.objects.create(
                property_obj=properties[i],
                tenant=tenant,
                lease_start_date="2024-01-01",
                lease_end_date="2024-12-31",
                monthly_rent=1000 + random.randint(0, 1000),
                deposit_amount=1000,
            )

    def measure_query_performance(self, queryset, description: str = ""):
        """Measure and log query performance."""
        import time
        from django.db import connection

        # Reset queries
        connection.queries_log.clear()

        start_time = time.time()
        result = list(queryset)  # Evaluate queryset
        end_time = time.time()

        execution_time = end_time - start_time
        query_count = len(connection.queries)

        print(f"📊 {description}")
        print(f"   Execution time: {execution_time:.4f}s")
        print(f"   Query count: {query_count}")
        print(f"   Result count: {len(result)}")

        return {
            "execution_time": execution_time,
            "query_count": query_count,
            "result_count": len(result),
        }


class SecurityTestCase(BaseTestCase):
    """Base test case for security testing."""

    def setUp(self):
        """Set up security test environment."""
        super().setUp()
        self.admin_user = self.create_user("admin", "admin@test.com", "admin")
        self.owner_user = self.create_user("owner", "owner@test.com", "owner")
        self.tenant_user = self.create_user("tenant", "tenant@test.com", "tenant")

    def test_permission_denied(self, user: User, url: str, method: str = "get", data: Optional[Dict] = None):
        """Test that a user gets permission denied for a resource."""
        self.authenticate_user(user)
        response = getattr(self.client, method)(url, data, format="json")
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_unauthenticated_access(self, url: str, method: str = "get", data: Optional[Dict] = None):
        """Test that unauthenticated requests are denied."""
        self.client.logout()
        response = getattr(self.client, method)(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuditTestMixin:
    """Mixin for testing audit logging."""

    def assert_audit_log_created(
        self,
        action: str,
        model_class: Type,
        obj_id: int,
        user: Optional[User] = None
    ):
        """Assert that an audit log entry was created."""
        from audit.models import AuditLog

        if user is None and hasattr(self, 'user'):
            user = self.user

        log_exists = AuditLog.objects.filter(
            user=user,
            action=action,
            content_type__model=model_class._meta.model_name,
            object_id=obj_id,
        ).exists()

        self.assertTrue(log_exists, f"Audit log not found for {action} on {model_class._meta.model_name}")

    def get_audit_logs(self, user: Optional[User] = None, limit: int = 10):
        """Get recent audit logs for testing."""
        from audit.models import AuditLog

        if user is None and hasattr(self, 'user'):
            user = self.user

        return AuditLog.objects.filter(user=user).order_by("-timestamp")[:limit]


# Test utilities
def assert_response_structure(test_case: TestCase, response, expected_fields: List[str]):
    """Assert that API response contains expected fields."""
    test_case.assertIsInstance(response.data, dict)
    for field in expected_fields:
        test_case.assertIn(field, response.data, f"Field '{field}' missing from response")


def assert_paginated_response(test_case: TestCase, response):
    """Assert that response is properly paginated."""
    assert_response_structure(test_case, response, ["count", "next", "previous", "results"])
    test_case.assertIsInstance(response.data["results"], list)


def create_test_image():
    """Create a test image file for testing file uploads."""
    from PIL import Image
    import io

    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    image_io = io.BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)

    return image_io