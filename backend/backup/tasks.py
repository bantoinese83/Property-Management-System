from celery import shared_task
from django.utils import timezone

from .services import BackupScheduler, BackupService


@shared_task
def run_scheduled_backups():
    """Run all due scheduled backups"""
    scheduler = BackupScheduler()
    backups = scheduler.run_scheduled_backups()

    return {
        'backups_created': len(backups),
        'backup_ids': [b.id for b in backups]
    }


@shared_task
def create_manual_backup(name: str, backup_type: str = 'full', user_id: int = None):
    """Create a manual backup"""
    service = BackupService()

    # Get user if provided
    user = None
    if user_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass

    backup = service.create_backup(
        name=name,
        backup_type=backup_type,
        user=user
    )

    return {
        'backup_id': backup.id,
        'status': backup.status,
        'file_path': backup.file_path
    }


@shared_task
def cleanup_old_backups(retention_days: int = 30):
    """Clean up old backups"""
    service = BackupService()
    deleted_count = service.cleanup_old_backups(retention_days)

    return {
        'deleted_backups': deleted_count
    }


@shared_task
def restore_from_backup(backup_id: int, user_id: int = None, tables: list = None, dry_run: bool = False):
    """Restore from a backup"""
    service = BackupService()

    # Get user if provided
    user = None
    if user_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass

    restore = service.restore_backup(
        backup_id=backup_id,
        user=user,
        tables=tables,
        dry_run=dry_run
    )

    return {
        'restore_id': restore.id,
        'status': restore.status,
        'records_restored': restore.records_restored,
        'tables_restored': restore.tables_restored
    }