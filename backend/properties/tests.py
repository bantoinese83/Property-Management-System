from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Property

User = get_user_model()


class PropertyModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="owner123", user_type="owner"
        )

        self.property = Property.objects.create(
            owner=self.owner,
            property_name="Test Property",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            property_type="apartment",
            total_units=5,
            purchase_price=Decimal("500000.00"),
        )

    def test_property_creation(self):
        """Test property creation"""
        self.assertEqual(self.property.property_name, "Test Property")
        self.assertEqual(self.property.owner, self.owner)
        self.assertEqual(self.property.total_units, 5)
        self.assertEqual(str(self.property), "Test Property - 123 Test St")

    def test_property_full_address(self):
        """Test full address property"""
        expected = "123 Test St, Test City, TS 12345"
        self.assertEqual(self.property.full_address, expected)

    def test_occupancy_rate_calculation(self):
        """Test occupancy rate calculation"""
        # No leases yet
        self.assertEqual(self.property.get_occupancy_rate(), 0)

        # Create a tenant and lease
        from leases.models import Lease
        from tenants.models import Tenant

        tenant = Tenant.objects.create(first_name="John", last_name="Doe", email="john@example.com")

        from datetime import date, timedelta
        today = date.today()
        lease = Lease.objects.create(
            property_obj=self.property,
            tenant=tenant,
            lease_start_date=today - timedelta(days=30),  # Started 30 days ago
            lease_end_date=today + timedelta(days=335),   # Ends in about a year
            monthly_rent=Decimal("2000.00"),
            status="active",
        )

        # Verify lease was created
        self.assertIsNotNone(lease.id)

        # Should have 20% occupancy (1 out of 5 units)
        self.assertEqual(self.property.get_occupancy_rate(), 20.0)


class PropertyAPITestCase(APITestCase):
    def setUp(self):
        # Use unique usernames to avoid conflicts between test runs
        import uuid
        unique_id = str(uuid.uuid4())[:8]

        self.owner = User.objects.create_user(
            username=f"owner_{unique_id}", email=f"owner_{unique_id}@example.com", password="owner123", user_type="owner"
        )

        self.other_user = User.objects.create_user(
            username=f"other_{unique_id}", email=f"other_{unique_id}@example.com", password="other123", user_type="owner"
        )

        self.property = Property.objects.create(
            owner=self.owner,
            property_name="Test Property",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            property_type="apartment",
            total_units=5,
        )

    def test_create_property(self):
        """Test creating a new property"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("property-list")
        data = {
            "property_name": "New Property",
            "address": "456 New St",
            "city": "New City",
            "state": "NS",
            "zip_code": "67890",
            "property_type": "single_family",
            "total_units": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["property_name"], "New Property")

    def test_list_properties(self):
        """Test listing properties for authenticated user"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("property-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_property_permissions(self):
        """Test that users can only see their own properties"""
        # Create property for other user
        other_property = Property.objects.create(
            owner=self.other_user,
            property_name="Other Property",
            address="789 Other St",
            city="Other City",
            state="OS",
            zip_code="98765",
            property_type="single_family",
            total_units=1,
        )

        # Verify other property was created
        self.assertIsNotNone(other_property.id)

        # Owner should only see their own property
        self.client.force_authenticate(user=self.owner)
        url = reverse("property-list")
        response = self.client.get(url)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["property_name"], "Test Property")

    def test_update_property(self):
        """Test updating a property"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("property-detail", kwargs={"pk": self.property.id})
        data = {
            "property_name": "Updated Property",
            "address": "123 Updated St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "property_type": "apartment",
            "total_units": 5,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["property_name"], "Updated Property")

    def test_delete_property(self):
        """Test deleting a property"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("property-detail", kwargs={"pk": self.property.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify property is deleted
        self.assertFalse(Property.objects.filter(id=self.property.id).exists())

    def test_occupancy_details(self):
        """Test getting occupancy details"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("property-occupancy-details", kwargs={"pk": self.property.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_units", response.data)
        self.assertIn("occupied_units", response.data)
        self.assertIn("occupancy_rate", response.data)
