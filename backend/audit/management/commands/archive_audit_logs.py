from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from audit.models import AuditLog, AuditLogArchive


class Command(BaseCommand):
    help = 'Archive old audit logs to reduce database size'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Archive logs older than this many days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be archived without actually doing it'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timedelta(days=days)

        # Get logs to archive
        logs_to_archive = AuditLog.objects.filter(timestamp__lt=cutoff_date)

        count = logs_to_archive.count()

        if dry_run:
            self.stdout.write(
                f"DRY RUN: Would archive {count} audit logs older than {cutoff_date.date()}"
            )
            return

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"No audit logs older than {cutoff_date.date()} to archive")
            )
            return

        # Archive the logs
        archived_count = 0
        for log in logs_to_archive:
            # Create archive record
            archive_data = {
                'id': log.id,
                'username': log.username,
                'user_id': log.user_id,
                'content_type_id': log.content_type_id,
                'object_id': log.object_id,
                'action': log.action,
                'action_description': log.action_description,
                'old_values': log.old_values,
                'new_values': log.new_values,
                'ip_address': str(log.ip_address) if log.ip_address else None,
                'user_agent': log.user_agent,
                'session_id': log.session_id,
                'timestamp': log.timestamp.isoformat(),
                'app_label': log.app_label,
                'model_name': log.model_name,
            }

            AuditLogArchive.objects.create(
                original_id=log.id,
                data=archive_data
            )

            # Delete original log
            log.delete()
            archived_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully archived {archived_count} audit logs older than {cutoff_date.date()}"
            )
        )