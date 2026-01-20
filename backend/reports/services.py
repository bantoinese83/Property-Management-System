import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from accounting.models import FinancialTransaction
from leases.models import Lease
from maintenance.models import MaintenanceRequest
from payments.models import RentPayment
from properties.models import Property
from tenants.models import Tenant

from .models import Report


class ReportService:
    """Service for generating various reports"""

    @staticmethod
    def generate_financial_summary_report(
        user, start_date: str, end_date: str, property_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive financial summary report"""

        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        # Base queryset filtered by user permissions
        if user.user_type == "admin":
            transactions = FinancialTransaction.objects.all()
            payments = RentPayment.objects.all()
            properties = Property.objects.all()
        else:
            transactions = FinancialTransaction.objects.filter(property_obj__owner=user)
            payments = RentPayment.objects.filter(lease_obj__property_obj__owner=user)
            properties = Property.objects.filter(owner=user)

        if property_ids:
            transactions = transactions.filter(property_obj_id__in=property_ids)
            payments = payments.filter(lease_obj__property_obj_id__in=property_ids)
            properties = properties.filter(id__in=property_ids)

        # Filter by date range
        transactions = transactions.filter(transaction_date__gte=start, transaction_date__lte=end)
        payments = payments.filter(payment_date__gte=start, payment_date__lte=end)

        # Calculate financial metrics
        income_total = transactions.filter(transaction_type="income").aggregate(total=Sum("amount"))["total"] or 0
        expense_total = transactions.filter(transaction_type="expense").aggregate(total=Sum("amount"))["total"] or 0
        rent_collected = payments.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0

        # Payment status breakdown
        payment_status = (
            payments.values("status").annotate(count=Count("id"), total_amount=Sum("amount")).order_by("status")
        )

        # Monthly breakdown
        monthly_data = []
        current_date = start
        while current_date <= end:
            month_start = current_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            month_income = (
                transactions.filter(
                    transaction_type="income", transaction_date__gte=month_start, transaction_date__lte=month_end
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            month_expenses = (
                transactions.filter(
                    transaction_type="expense", transaction_date__gte=month_start, transaction_date__lte=month_end
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            month_rent = (
                payments.filter(payment_date__gte=month_start, payment_date__lte=month_end, status="paid").aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

            monthly_data.append(
                {
                    "month": month_start.strftime("%B %Y"),
                    "income": float(month_income),
                    "expenses": float(month_expenses),
                    "rent_collected": float(month_rent),
                    "net_profit": float(month_income + month_rent - month_expenses),
                }
            )

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        # Top expense categories
        expense_categories = (
            transactions.filter(transaction_type="expense")
            .values("category")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")[:10]
        )

        return {
            "report_type": "Financial Summary",
            "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "summary": {
                "total_income": float(income_total),
                "total_expenses": float(expense_total),
                "rent_collected": float(rent_collected),
                "net_profit": float(income_total + rent_collected - expense_total),
                "profit_margin": float(
                    (income_total + rent_collected - expense_total) / max(income_total + rent_collected, 1) * 100
                ),
            },
            "payment_status_breakdown": list(payment_status),
            "monthly_breakdown": monthly_data,
            "top_expense_categories": list(expense_categories),
            "property_count": properties.count(),
            "generated_at": timezone.now().isoformat(),
            "generated_by": user.get_full_name(),
        }

    @staticmethod
    def generate_property_performance_report(
        user, start_date: str, end_date: str, property_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Generate property performance analysis report"""

        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        # Get properties
        if user.user_type == "admin":
            properties = Property.objects.all()
        else:
            properties = Property.objects.filter(owner=user)

        if property_ids:
            properties = properties.filter(id__in=property_ids)

        property_data = []
        for prop in properties:
            # Financial performance
            transactions = FinancialTransaction.objects.filter(
                property_obj=prop, transaction_date__gte=start, transaction_date__lte=end
            )

            payments = RentPayment.objects.filter(
                lease_obj__property_obj=prop, payment_date__gte=start, payment_date__lte=end
            )

            income = transactions.filter(transaction_type="income").aggregate(total=Sum("amount"))["total"] or 0
            expenses = transactions.filter(transaction_type="expense").aggregate(total=Sum("amount"))["total"] or 0
            rent_collected = payments.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0

            # Occupancy data
            active_leases = Lease.objects.filter(
                property_obj=prop, status="active", lease_start_date__lte=end, lease_end_date__gte=start
            )

            occupancy_rate = prop.get_occupancy_rate()

            # Maintenance data
            maintenance_requests = MaintenanceRequest.objects.filter(
                property_obj=prop, requested_date__gte=start, requested_date__lte=end
            )

            avg_resolution_time = 0
            if maintenance_requests.filter(status="completed").exists():
                completed_requests = maintenance_requests.filter(status="completed")
                total_resolution_time = sum(
                    (req.completed_date - req.requested_date).days for req in completed_requests if req.completed_date
                )
                avg_resolution_time = total_resolution_time / completed_requests.count()

            property_data.append(
                {
                    "property_id": prop.id,
                    "property_name": prop.property_name,
                    "address": prop.full_address,
                    "property_type": prop.property_type,
                    "total_units": prop.total_units,
                    "occupancy_rate": occupancy_rate,
                    "active_leases": active_leases.count(),
                    "total_income": float(income + rent_collected),
                    "total_expenses": float(expenses),
                    "net_profit": float(income + rent_collected - expenses),
                    "maintenance_requests": maintenance_requests.count(),
                    "maintenance_completed": maintenance_requests.filter(status="completed").count(),
                    "avg_maintenance_resolution_days": round(avg_resolution_time, 1),
                    "roi_percentage": float(
                        (income + rent_collected - expenses) / max(prop.purchase_price or 1, 1) * 100
                    ),
                }
            )

        # Sort by net profit descending
        property_data.sort(key=lambda x: x["net_profit"], reverse=True)

        return {
            "report_type": "Property Performance Analysis",
            "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "summary": {
                "total_properties": len(property_data),
                "average_occupancy": sum(p["occupancy_rate"] for p in property_data) / max(len(property_data), 1),
                "total_income": sum(p["total_income"] for p in property_data),
                "total_expenses": sum(p["total_expenses"] for p in property_data),
                "total_profit": sum(p["net_profit"] for p in property_data),
            },
            "property_performance": property_data,
            "generated_at": timezone.now().isoformat(),
            "generated_by": user.get_full_name(),
        }

    @staticmethod
    def generate_tenant_report(
        user, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive tenant report"""

        # Get tenants
        if user.user_type == "admin":
            tenants = Tenant.objects.all()
        else:
            tenants = Tenant.objects.filter(leases__property__owner=user).distinct()

        tenant_data = []
        for tenant in tenants:
            active_leases = tenant.get_active_leases()
            monthly_rent = tenant.get_monthly_rent_total()

            # Payment history
            payments = RentPayment.objects.filter(lease_obj__tenant=tenant)
            total_paid = payments.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0
            total_overdue = payments.filter(status="overdue").aggregate(total=Sum("amount"))["total"] or 0

            # Maintenance requests
            maintenance = MaintenanceRequest.objects.filter(tenant=tenant)
            total_requests = maintenance.count()
            completed_requests = maintenance.filter(status="completed").count()

            tenant_data.append(
                {
                    "tenant_id": tenant.id,
                    "full_name": tenant.full_name,
                    "email": tenant.email,
                    "phone": tenant.phone,
                    "address": f"{tenant.city}, {tenant.state}",
                    "is_active": tenant.is_active,
                    "credit_score": tenant.credit_score,
                    "annual_income": float(tenant.annual_income or 0),
                    "active_leases": active_leases.count(),
                    "monthly_rent_total": float(monthly_rent),
                    "total_paid": float(total_paid),
                    "total_overdue": float(total_overdue),
                    "payment_history_count": payments.count(),
                    "on_time_payment_rate": (
                        payments.filter(status="paid", payment_date__lte=models.F("due_date")).count()
                        / max(payments.count(), 1)
                        * 100
                    ),
                    "maintenance_requests": total_requests,
                    "maintenance_completed": completed_requests,
                    "lease_start_date": active_leases[0].lease_start_date.isoformat() if active_leases else None,
                }
            )

        return {
            "report_type": "Tenant Report",
            "summary": {
                "total_tenants": len(tenant_data),
                "active_tenants": sum(1 for t in tenant_data if t["is_active"]),
                "total_monthly_revenue": sum(t["monthly_rent_total"] for t in tenant_data),
                "average_credit_score": sum(t["credit_score"] for t in tenant_data if t["credit_score"])
                / max(sum(1 for t in tenant_data if t["credit_score"]), 1),
            },
            "tenant_data": tenant_data,
            "generated_at": timezone.now().isoformat(),
            "generated_by": user.get_full_name(),
        }

    @staticmethod
    def generate_maintenance_report(
        user, start_date: str, end_date: str, property_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Generate maintenance analysis report"""

        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        # Get maintenance requests
        if user.user_type == "admin":
            requests = MaintenanceRequest.objects.all()
        else:
            requests = MaintenanceRequest.objects.filter(property_obj__owner=user)

        if property_ids:
            requests = requests.filter(property_obj_id__in=property_ids)

        requests = requests.filter(requested_date__gte=start, requested_date__lte=end)

        # Category breakdown
        category_stats = (
            requests.values("category")
            .annotate(
                total_requests=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                avg_cost=Avg("actual_cost", filter=Q(actual_cost__isnull=False)),
                urgent_count=Count("id", filter=Q(priority="urgent")),
            )
            .order_by("-total_requests")
        )

        # Priority analysis
        priority_stats = requests.values("priority").annotate(
            count=Count("id"),
            avg_resolution_days=Avg(
                models.F("completed_date") - models.F("requested_date"),
                filter=Q(status="completed", completed_date__isnull=False),
            ),
        )

        # Monthly trends
        monthly_trends = []
        current_date = start
        while current_date <= end:
            month_requests = requests.filter(
                requested_date__year=current_date.year, requested_date__month=current_date.month
            )

            monthly_trends.append(
                {
                    "month": current_date.strftime("%B %Y"),
                    "total_requests": month_requests.count(),
                    "completed": month_requests.filter(status="completed").count(),
                    "urgent": month_requests.filter(priority="urgent").count(),
                    "avg_resolution_days": (
                        month_requests.filter(status="completed", completed_date__isnull=False)
                        .aggregate(avg_days=Avg(models.F("completed_date") - models.F("requested_date")))["avg_days"]
                        .days
                        if month_requests.filter(status="completed", completed_date__isnull=False).exists()
                        else 0
                    ),
                }
            )

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return {
            "report_type": "Maintenance Analysis Report",
            "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "summary": {
                "total_requests": requests.count(),
                "completed_requests": requests.filter(status="completed").count(),
                "pending_requests": requests.filter(status__in=["open", "assigned"]).count(),
                "urgent_requests": requests.filter(priority="urgent").count(),
                "average_resolution_days": (
                    requests.filter(status="completed", completed_date__isnull=False)
                    .aggregate(avg_days=Avg(models.F("completed_date") - models.F("requested_date")))["avg_days"]
                    .days
                    if requests.filter(status="completed", completed_date__isnull=False).exists()
                    else 0
                ),
            },
            "category_breakdown": list(category_stats),
            "priority_analysis": list(priority_stats),
            "monthly_trends": monthly_trends,
            "generated_at": timezone.now().isoformat(),
            "generated_by": user.get_full_name(),
        }
