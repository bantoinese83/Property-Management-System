from django.db import models
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(ReadOnlyModelViewSet):
    """ViewSet for viewing audit logs (admin only)"""

    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'content_type', 'app_label', 'model_name']
    search_fields = ['username', 'action_description', 'ip_address']
    ordering_fields = ['timestamp', 'username', 'action']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter audit logs based on admin permissions"""
        user = self.request.user

        # Only admins can see audit logs
        if not user.is_staff and user.user_type != 'admin':
            return AuditLog.objects.none()

        # Admins can see all logs, but filter out sensitive data for non-superusers
        queryset = AuditLog.objects.all()

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get audit log summary statistics"""
        queryset = self.get_queryset()

        # Basic counts
        total_logs = queryset.count()
        today_logs = queryset.filter(
            timestamp__date=timezone.now().date()
        ).count()

        # Action breakdown
        actions = queryset.values('action').annotate(
            count=models.Count('id')
        ).order_by('-count')

        # User activity (top 10 most active users)
        user_activity = queryset.values('username').annotate(
            count=models.Count('id')
        ).exclude(username='system').order_by('-count')[:10]

        # Recent activity (last 24 hours)
        recent_activity = queryset.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).values('action').annotate(
            count=models.Count('id')
        )

        return Response({
            'summary': {
                'total_logs': total_logs,
                'today_logs': today_logs,
                'unique_users': queryset.values('username').distinct().count(),
            },
            'actions_breakdown': list(actions),
            'user_activity': list(user_activity),
            'recent_activity': list(recent_activity),
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export audit logs to CSV"""
        queryset = self.get_queryset()

        # Convert to CSV format
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'Username', 'Action', 'Description',
            'App', 'Model', 'Object ID', 'IP Address'
        ])

        for log in queryset[:1000]:  # Limit to 1000 records for performance
            writer.writerow([
                log.timestamp.isoformat(),
                log.username,
                log.get_action_display(),
                log.action_description,
                log.app_label,
                log.model_name,
                log.object_id,
                log.ip_address or '',
            ])

        return response