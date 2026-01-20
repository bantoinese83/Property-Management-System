from django.core.management.base import BaseCommand

from reports.models import ReportTemplate


class Command(BaseCommand):
    help = "Create default report templates"

    def handle(self, *args, **options):
        templates = [
            {
                "name": "monthly_financial_summary",
                "display_name": "Monthly Financial Summary",
                "description": "Comprehensive overview of income, expenses, and profitability for the month",
                "report_type": "financial_summary",
                "category": "financial",
                "default_parameters": {"date_range": "month"},
                "sort_order": 1,
            },
            {
                "name": "quarterly_financial_report",
                "display_name": "Quarterly Financial Report",
                "description": "Detailed quarterly financial analysis with trends and comparisons",
                "report_type": "financial_summary",
                "category": "financial",
                "default_parameters": {"date_range": "quarter"},
                "sort_order": 2,
            },
            {
                "name": "property_performance_analysis",
                "display_name": "Property Performance Analysis",
                "description": "Compare performance metrics across all properties",
                "report_type": "property_performance",
                "category": "property",
                "default_parameters": {"include_roi": True, "include_maintenance": True},
                "sort_order": 3,
            },
            {
                "name": "tenant_portfolio_report",
                "display_name": "Tenant Portfolio Report",
                "description": "Complete overview of all tenants including payment history and lease details",
                "report_type": "tenant_report",
                "category": "tenant",
                "default_parameters": {"include_payment_history": True, "include_credit_scores": True},
                "sort_order": 4,
            },
            {
                "name": "maintenance_efficiency_report",
                "display_name": "Maintenance Efficiency Report",
                "description": "Analysis of maintenance requests, response times, and cost efficiency",
                "report_type": "maintenance_report",
                "category": "maintenance",
                "default_parameters": {"include_resolution_times": True, "include_cost_analysis": True},
                "sort_order": 5,
            },
            {
                "name": "yearly_tax_report",
                "display_name": "Yearly Tax Report",
                "description": "Comprehensive annual report for tax preparation and accounting",
                "report_type": "financial_summary",
                "category": "tax",
                "default_parameters": {"date_range": "year", "include_all_properties": True},
                "sort_order": 6,
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = ReportTemplate.objects.get_or_create(name=template_data["name"], defaults=template_data)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created template: {template.display_name}"))
            else:
                # Update existing template
                for key, value in template_data.items():
                    setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated template: {template.display_name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {created_count + updated_count} report templates "
                f"({created_count} created, {updated_count} updated)"
            )
        )
