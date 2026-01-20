from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from leases.models import Lease
from properties.models import Property
from tenants.models import Tenant
from users.models import User


class Command(BaseCommand):
    help = "Create demo data for testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating demo data...")

        # Create admin user
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "user_type": "admin",
                "first_name": "Admin",
                "last_name": "User",
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("✓ Admin user created"))

        # Create owner user
        owner, created = User.objects.get_or_create(
            username="owner",
            defaults={
                "email": "owner@example.com",
                "user_type": "owner",
                "first_name": "Property",
                "last_name": "Owner",
            },
        )
        if created:
            owner.set_password("owner123")
            owner.save()
            self.stdout.write(self.style.SUCCESS("✓ Owner user created"))

        # Create property
        property_obj, created = Property.objects.get_or_create(
            owner=owner,
            address="123 Main St",
            defaults={
                "property_name": "Downtown Apartment",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "property_type": "apartment",
                "total_units": 5,
                "purchase_price": 500000,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Property created"))

        # Create tenant
        tenant, created = Tenant.objects.get_or_create(
            email="tenant@example.com",
            defaults={
                "first_name": "John",
                "last_name": "Doe",
                "phone": "555-0123",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Tenant created"))

        # Create lease
        today = timezone.now().date()
        lease, created = Lease.objects.get_or_create(
            property_obj=property_obj,
            tenant=tenant,
            lease_start_date=today,
            defaults={
                "lease_end_date": today + timedelta(days=365),
                "monthly_rent": 2000,
                "deposit_amount": 4000,
                "status": "active",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Lease created"))

        self.stdout.write(self.style.SUCCESS("Demo data created successfully!"))
