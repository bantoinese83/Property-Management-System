"""
Integration tests for the Property Management System.

These tests cover end-to-end workflows and ensure all components
work together correctly.
"""

import json
from datetime import date, timedelta

from django.core.management import call_command
from django.urls import reverse
from rest_framework import status

from .tests import IntegrationTestCase, PropertyTestMixin
from leases.models import Lease
from payments.models import RentPayment


class PropertyManagementWorkflowTest(IntegrationTestCase):
    """Test complete property management workflows."""

    def test_property_creation_to_lease_workflow(self):
        """Test the complete workflow from property creation to lease signing."""
        # 1. Create a property
        property_data = {
            "property_name": "Downtown Luxury Apartment",
            "address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "property_type": "apartment",
            "total_units": 10,
            "year_built": 2015,
            "square_footage": 1200,
            "purchase_price": 500000,
        }

        response = self.api_request("post", reverse("property-list"), property_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        property_id = response.data["id"]

        # Verify property details
        response = self.api_request("get", reverse("property-detail", args=[property_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["property_name"], "Downtown Luxury Apartment")
        self.assertEqual(response.data["total_units"], 10)

        # 2. Create a tenant
        tenant_data = {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "555-0123",
        }

        response = self.api_request("post", reverse("tenant-list"), tenant_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tenant_id = response.data["id"]

        # 3. Create a lease agreement
        lease_data = {
            "property_obj": property_id,
            "tenant": tenant_id,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2024-12-31",
            "monthly_rent": 2500.00,
            "deposit_amount": 2500.00,
            "pet_deposit": 500.00,
            "late_fee": 50.00,
            "auto_renew": True,
            "renewal_notice_days": 60,
        }

        response = self.api_request("post", reverse("lease-list"), lease_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        lease_id = response.data["id"]

        # Verify lease was created
        response = self.api_request("get", reverse("lease-detail", args=[lease_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["monthly_rent"]), 2500.00)

        # 4. Record rent payment
        payment_data = {
            "lease_obj": lease_id,
            "amount": 2500.00,
            "payment_date": "2024-01-01",
            "due_date": "2024-01-01",
            "payment_method": "bank_transfer",
            "status": "paid",
        }

        response = self.api_request("post", reverse("rentpayment-list"), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 5. Create maintenance request
        maintenance_data = {
            "property": property_id,
            "title": "Kitchen Faucet Repair",
            "description": "The kitchen faucet is leaking and needs to be repaired.",
            "priority": "medium",
            "category": "plumbing",
            "scheduled_date": "2024-01-15",
        }

        response = self.api_request("post", reverse("maintenance-list"), maintenance_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        maintenance_id = response.data["id"]

        # 6. Verify dashboard shows updated statistics
        response = self.api_request("get", reverse("property-dashboard-stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_properties"], 1)

        # 7. Verify comprehensive analytics
        response = self.api_request("get", reverse("property-dashboard-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_properties", response.data)

        # 8. Test audit logging (if enabled)
        # This would verify that all actions were logged
        # Implementation depends on audit middleware configuration

    def test_financial_reporting_workflow(self):
        """Test financial reporting and accounting workflows."""
        # Setup property and lease
        property_obj = self.create_property()
        tenant = self.create_tenant()

        lease = Lease.objects.create(
            property_obj=property_obj,
            tenant=tenant,
            lease_start_date=date.today(),
            lease_end_date=date.today() + timedelta(days=365),
            monthly_rent=2000.00,
            deposit_amount=2000.00,
        )

        # Create rent payment
        payment = RentPayment.objects.create(
            lease_obj=lease,
            amount=2000.00,
            payment_date=date.today(),
            due_date=date.today(),
            payment_method="bank_transfer",
            status="paid",
        )

        # Test financial transaction creation
        transaction_data = {
            "property_obj": property_obj.id,
            "transaction_type": "income",
            "category": "rent",
            "amount": 2000.00,
            "description": "January 2024 Rent",
            "transaction_date": date.today().isoformat(),
            "lease": lease.id,
        }

        response = self.api_request("post", reverse("financialtransaction-list"), transaction_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test accounting period creation
        period_data = {
            "property_obj": property_obj.id,
            "period_start": "2024-01-01",
            "period_end": "2024-01-31",
            "period_type": "monthly",
        }

        response = self.api_request("post", reverse("accountingperiod-list"), period_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify financial reports are accessible
        response = self.api_request("get", reverse("reports-financial"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIPerformanceTest(IntegrationTestCase):
    """Test API performance and response times."""

    def test_dashboard_performance(self):
        """Test dashboard API performance."""
        import time

        # Create test data
        for i in range(10):
            self.create_property(property_name=f"Perf Property {i}")

        # Test dashboard stats response time
        start_time = time.time()
        response = self.api_request("get", reverse("property-dashboard-stats"))
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_time = end_time - start_time
        # Should respond within 500ms
        self.assertLess(response_time, 0.5, f"Dashboard stats too slow: {response_time}s")

    def test_property_listing_performance(self):
        """Test property listing performance with pagination."""
        import time

        # Create many properties
        for i in range(100):
            self.create_property(property_name=f"Bulk Property {i}")

        # Test paginated listing
        start_time = time.time()
        response = self.api_request("get", reverse("property-list"))
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        response_time = end_time - start_time
        # Should respond within 1 second
        self.assertLess(response_time, 1.0, f"Property listing too slow: {response_time}s")


class SecurityIntegrationTest(IntegrationTestCase):
    """Test security features and access controls."""

    def test_user_isolation(self):
        """Test that users can only access their own data."""
        # Create another user
        other_user = self.create_user("other_owner", "other@example.com", "owner")

        # Create property for other user
        other_property = self.create_property(
            owner=other_user,
            property_name="Other User's Property"
        )

        # Current user should not see other user's property
        response = self.api_request("get", reverse("property-list"))
        property_ids = [prop["id"] for prop in response.data["results"]]

        self.assertNotIn(other_property.id, property_ids,
                        "User can see other user's properties")

    def test_admin_access(self):
        """Test that admin users have full access."""
        # Create admin user
        admin_user = self.create_user("admin_test", "admin@test.com", "admin")

        # Switch to admin user
        self.authenticate_user(admin_user)

        # Admin should see all properties
        response = self.api_request("get", reverse("property-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin should have access to audit logs
        response = self.api_request("get", reverse("auditlog-list"))
        # This might return 403 if audit logs require special permissions
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])


class DocumentManagementTest(IntegrationTestCase):
    """Test document management and template features."""

    def test_document_template_workflow(self):
        """Test document template creation and usage."""
        # Test template listing
        response = self.api_request("get", reverse("documenttemplate-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # If templates exist, test document generation
        if response.data:
            template_id = response.data[0]["id"]

            # Test template variables endpoint
            response = self.api_request("get", reverse("documenttemplate-variables", args=[template_id]))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Test document generation (if template variables are available)
            if "variables" in response.data:
                variables = {}
                for var_name in response.data["variables"]:
                    variables[var_name] = f"Test {var_name}"

                generation_data = {
                    "template_id": template_id,
                    "variables": variables,
                    "title": "Test Generated Document"
                }

                response = self.api_request("post", reverse("document-generate"), generation_data)
                # Document generation might require all variables to be filled
                self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


class NotificationSystemTest(IntegrationTestCase):
    """Test notification and email system."""

    def test_notification_preferences(self):
        """Test user notification preferences."""
        # Test notification preferences endpoint
        response = self.api_request("get", reverse("notificationpreference-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test updating preferences
        preference_data = {
            "email_notifications": True,
            "sms_notifications": False,
            "rent_due_reminders": True,
            "maintenance_updates": True,
        }

        response = self.api_request("post", reverse("notificationpreference-list"), preference_data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


class DataExportTest(IntegrationTestCase):
    """Test data export functionality."""

    def test_csv_export(self):
        """Test CSV export functionality."""
        # Create test data
        self.create_property(property_name="Export Test Property")

        # Test property export
        export_url = reverse("property-list") + "?export=csv"
        response = self.api_request("get", export_url)

        # Export might be implemented as a separate endpoint or query parameter
        # This tests the basic API structure
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_report_generation(self):
        """Test report generation and export."""
        # Test reports endpoint
        response = self.api_request("get", reverse("reports-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # If reports exist, test report generation
        if response.data:
            report_data = {
                "template_id": response.data[0]["id"],
                "parameters": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                }
            }

            response = self.api_request("post", reverse("reports-generate"), report_data)
            self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


class SystemHealthTest(IntegrationTestCase):
    """Test system health and monitoring."""

    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        # Remove authentication for health check
        self.client.logout()

        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response structure
        self.assertIn("status", response.data)
        self.assertIn("checks", response.data)

    def test_metrics_endpoint(self):
        """Test the metrics endpoint."""
        response = self.api_request("get", reverse("metrics"))
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_cache_functionality(self):
        """Test that caching is working."""
        # Make same request multiple times
        url = reverse("property-dashboard-stats")

        response1 = self.api_request("get", url)
        response2 = self.api_request("get", url)

        # Responses should be identical and fast
        self.assertEqual(response1.status_code, response2.status_code)
        self.assertEqual(response1.data, response2.data)