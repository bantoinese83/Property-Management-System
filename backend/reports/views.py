import json
import os

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Report, ReportTemplate
from .services import ReportService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """Generate a report based on provided parameters"""
    try:
        report_type = request.data.get("report_type")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        property_ids = request.data.get("property_ids", [])
        title = request.data.get("title", f'{report_type.replace("_", " ").title()} Report')

        if not report_type or not start_date or not end_date:
            return Response(
                {"error": "report_type, start_date, and end_date are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Generate report data based on type
        if report_type == "financial_summary":
            report_data = ReportService.generate_financial_summary_report(
                request.user, start_date, end_date, property_ids
            )
        elif report_type == "property_performance":
            report_data = ReportService.generate_property_performance_report(
                request.user, start_date, end_date, property_ids
            )
        elif report_type == "tenant_report":
            report_data = ReportService.generate_tenant_report(request.user)
        elif report_type == "maintenance_report":
            report_data = ReportService.generate_maintenance_report(request.user, start_date, end_date, property_ids)
        else:
            return Response({"error": f"Unknown report type: {report_type}"}, status=status.HTTP_400_BAD_REQUEST)

        # Save report to database
        report = Report.objects.create(
            title=title,
            report_type=report_type,
            description=f"Generated report for {start_date} to {end_date}",
            parameters={"start_date": start_date, "end_date": end_date, "property_ids": property_ids},
            status="completed",
            created_by=request.user,
            start_date=start_date,
            end_date=end_date,
            file_path="",  # Could save to file if needed
        )

        # Return report data
        return Response({"report_id": report.id, "data": report_data, "status": "completed"})

    except Exception as e:
        return Response({"error": f"Failed to generate report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_reports(request):
    """List user's generated reports"""
    try:
        if request.user.user_type == "admin":
            reports = Report.objects.all()
        else:
            reports = Report.objects.filter(created_by=request.user)

        reports_data = []
        for report in reports.order_by("-created_at")[:50]:  # Limit to last 50 reports
            reports_data.append(
                {
                    "id": report.id,
                    "title": report.title,
                    "report_type": report.report_type,
                    "status": report.status,
                    "created_at": report.created_at.isoformat(),
                    "start_date": report.start_date.isoformat() if report.start_date else None,
                    "end_date": report.end_date.isoformat() if report.end_date else None,
                    "is_ready": report.is_ready,
                    "download_count": report.download_count,
                }
            )

        return Response({"reports": reports_data})

    except Exception as e:
        return Response({"error": f"Failed to list reports: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_report_templates(request):
    """Get available report templates"""
    try:
        templates = ReportTemplate.objects.filter(is_active=True)

        templates_data = []
        for template in templates:
            templates_data.append(
                {
                    "id": template.id,
                    "name": template.name,
                    "display_name": template.display_name,
                    "description": template.description,
                    "report_type": template.report_type,
                    "category": template.category,
                    "default_parameters": template.default_parameters,
                }
            )

        return Response({"templates": templates_data})

    except Exception as e:
        return Response(
            {"error": f"Failed to get report templates: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_report(request, report_id):
    """Delete a report"""
    try:
        if request.user.user_type == "admin":
            report = Report.objects.get(id=report_id)
        else:
            report = Report.objects.get(id=report_id, created_by=request.user)

        # Delete associated file if it exists
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)

        report.delete()

        return Response({"message": "Report deleted successfully"})

    except Report.DoesNotExist:
        return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Failed to delete report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
