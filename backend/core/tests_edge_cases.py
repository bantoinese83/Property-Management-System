"""
Edge cases and boundary condition tests for the Property Management System.

This module contains comprehensive tests for edge cases including:
- Boundary value testing
- Invalid input handling
- Error condition testing
- Performance edge cases
- Security edge cases
"""

import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from leases.models import Lease
from payments.models import RentPayment
from properties.models import Property
from tenants.models import Tenant


class EdgeCasesTestCase(TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Set up test data"""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            user_type="owner"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_file_upload_edge_cases(self):
        """Test file upload edge cases"""
        # Test empty file
        empty_file = SimpleUploadedFile("empty.txt", b"", content_type="text/plain")
        response = self.client.post("/api/documents/", {
            "title": "Empty File",
            "model_name": "property",
            "object_id": 1,
            "file": empty_file
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test oversized file (simulate > 10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")
        response = self.client.post("/api/documents/", {
            "title": "Large File",
            "model_name": "property",
            "object_id": 1,
            "file": large_file
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test dangerous file extension
        exe_file = SimpleUploadedFile("malicious.exe", b"fake exe content", content_type="application/octet-stream")
        response = self.client.post("/api/documents/", {
            "title": "EXE File",
            "model_name": "property",
            "object_id": 1,
            "file": exe_file
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_property_validation_edge_cases(self):
        """Test property validation edge cases"""
        # Test invalid year_built
        response = self.client.post("/api/properties/", {
            "property_name": "Test Property",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "single_family",
            "total_units": 1,
            "year_built": 1700  # Too old
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("year_built", response.data)

        # Test future year_built
        future_year = date.today().year + 2
        response = self.client.post("/api/properties/", {
            "property_name": "Test Property",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "single_family",
            "total_units": 1,
            "year_built": future_year
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid latitude/longitude
        response = self.client.post("/api/properties/", {
            "property_name": "Test Property",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "single_family",
            "total_units": 1,
            "latitude": 91,  # Invalid latitude
            "longitude": 0
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lease_validation_edge_cases(self):
        """Test lease validation edge cases"""
        # Create a property first
        property_obj = Property.objects.create(
            owner=self.user,
            property_name="Test Property",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            property_type="single_family",
            total_units=1
        )

        # Create a tenant
        tenant = Tenant.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )

        # Test lease with end date before start date
        response = self.client.post("/api/leases/", {
            "property_obj": property_obj.id,
            "tenant": tenant.id,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2023-12-31",  # Before start date
            "monthly_rent": 1000
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test lease duration too short
        response = self.client.post("/api/leases/", {
            "property_obj": property_obj.id,
            "tenant": tenant.id,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2024-01-15",  # Only 14 days
            "monthly_rent": 1000
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test negative rent
        response = self.client.post("/api/leases/", {
            "property_obj": property_obj.id,
            "tenant": tenant.id,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2025-01-01",
            "monthly_rent": -1000
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_logic_edge_cases(self):
        """Test business logic edge cases"""
        # Create property with 0 units
        property_obj = Property.objects.create(
            owner=self.user,
            property_name="Empty Property",
            address="123 Empty St",
            city="Empty City",
            state="ES",
            zip_code="12345",
            property_type="single_family",
            total_units=0  # Edge case: no units
        )

        # Test occupancy rate calculation with 0 units
        occupancy_rate = property_obj.get_occupancy_rate()
        self.assertEqual(occupancy_rate, 0.0)

        # Test with very large numbers
        large_property = Property.objects.create(
            owner=self.user,
            property_name="Large Property",
            address="456 Large St",
            city="Large City",
            state="LS",
            zip_code="12345",
            property_type="apartment",
            total_units=10000  # Very large building
        )

        # Test monthly income with large property
        income = large_property.get_monthly_income()
        self.assertEqual(income, 0)  # No leases yet

    def test_date_edge_cases(self):
        """Test date-related edge cases"""
        # Create property
        property_obj = Property.objects.create(
            owner=self.user,
            property_name="Date Test Property",
            address="123 Date St",
            city="Date City",
            state="DS",
            zip_code="12345",
            property_type="single_family",
            total_units=1
        )

        tenant = Tenant.objects.create(
            first_name="Date",
            last_name="Test",
            email="date@example.com"
        )

        # Test lease with dates far in the future
        far_future = date.today() + timedelta(days=365*20)  # 20 years
        response = self.client.post("/api/leases/", {
            "property_obj": property_obj.id,
            "tenant": tenant.id,
            "lease_start_date": (date.today() + timedelta(days=365*2)).isoformat(),
            "lease_end_date": far_future.isoformat(),
            "monthly_rent": 1000
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Should fail due to end date too far

    def test_concurrency_edge_cases(self):
        """Test optimistic locking and concurrency"""
        # Create a property
        property_obj = Property.objects.create(
            owner=self.user,
            property_name="Concurrency Test",
            address="123 Concurrency St",
            city="Concurrency City",
            state="CS",
            zip_code="12345",
            property_type="single_family",
            total_units=1
        )

        # Test version increment on save
        original_version = property_obj.version
        property_obj.property_name = "Updated Name"
        property_obj.save()
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.version, original_version + 1)

    def test_null_empty_edge_cases(self):
        """Test null and empty value handling"""
        # Test property with minimal required fields
        response = self.client.post("/api/properties/", {
            "property_name": "Minimal Property",
            "address": "123 Minimal St",
            "city": "Minimal City",
            "state": "MS",
            "zip_code": "12345",
            "property_type": "single_family",
            "total_units": 1
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test with empty strings that should fail
        response = self.client.post("/api/properties/", {
            "property_name": "",  # Empty name
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "single_family",
            "total_units": 1
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculation_edge_cases(self):
        """Test calculation edge cases"""
        # Create property
        property_obj = Property.objects.create(
            owner=self.user,
            property_name="Calc Test Property",
            address="123 Calc St",
            city="Calc City",
            state="CS",
            zip_code="12345",
            property_type="single_family",
            total_units=1
        )

        tenant = Tenant.objects.create(
            first_name="Calc",
            last_name="Test",
            email="calc@example.com"
        )

        # Create lease with very high rent
        lease = Lease.objects.create(
            property_obj=property_obj,
            tenant=tenant,
            lease_start_date=date.today() - timedelta(days=30),
            lease_end_date=date.today() + timedelta(days=335),
            monthly_rent=Decimal("1000000"),  # Very high rent
            status="active"
        )

        # Test calculations handle large numbers
        income = property_obj.get_monthly_income()
        self.assertEqual(income, Decimal("1000000"))

        occupancy = property_obj.get_occupancy_rate()
        self.assertEqual(occupancy, 100.0)  # 1 active lease out of 1 unit

    def test_string_validation_edge_cases(self):
        """Test string validation edge cases"""
        # Test very long strings
        long_name = "A" * 300  # Longer than max_length
        response = self.client.post("/api/properties/", {
            "property_name": long_name,
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "single_family",
            "total_units": 1
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid ZIP code
        response = self.client.post("/api/properties/", {
            "property_name": "Test Property",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "123456789",  # Invalid ZIP
            "property_type": "single_family",
            "total_units": 1
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)