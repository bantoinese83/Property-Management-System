import gzip
import hashlib
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.management import call_command
from django.db import connection, transaction
from django.utils import timezone

from .models import Backup, BackupRestore, BackupSchedule


class BackupService:
    """Service for handling database backups"""

    def __init__(self):
        self.backup_dir = getattr(settings, "BACKUP_DIR", "backups")
        self.max_retries = getattr(settings, "BACKUP_MAX_RETRIES", 3)

        # Create backup directory if it doesn't exist
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)

    def create_backup(
        self, name: str, backup_type: str = "full", user=None, tables: Optional[List[str]] = None
    ) -> Backup:
        """Create a database backup"""

        backup = Backup.objects.create(
            name=name,
            backup_type=backup_type,
            status="pending",
            created_by=user,
            tables_included=tables or self._get_all_tables(),
            started_at=timezone.now(),
        )

        try:
            backup.status = "in_progress"
            backup.save()

            # Generate backup file
            file_path = self._generate_backup_file(backup, tables)

            # Update backup metadata
            backup.file_path = file_path
            backup.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            backup.checksum = self._calculate_checksum(file_path)
            backup.record_count = self._count_records(tables)
            backup.status = "completed"
            backup.completed_at = timezone.now()
            backup.duration = backup.completed_at - backup.started_at

        except Exception as e:
            backup.status = "failed"
            backup.error_message = str(e)
            backup.completed_at = timezone.now()
            if backup.started_at:
                backup.duration = backup.completed_at - backup.started_at

        backup.save()
        return backup

    def restore_backup(
        self, backup_id: int, user=None, tables: Optional[List[str]] = None, dry_run: bool = False
    ) -> BackupRestore:
        """Restore from a backup"""

        try:
            backup = Backup.objects.get(id=backup_id, status="completed")
        except Backup.DoesNotExist:
            raise ValueError("Backup not found or not completed")

        restore = BackupRestore.objects.create(
            backup=backup,
            status="pending" if not dry_run else "in_progress",
            tables_to_restore=tables or backup.tables_included,
            dry_run=dry_run,
            created_by=user,
            started_at=timezone.now(),
        )

        try:
            if not dry_run:
                restore.status = "in_progress"
                restore.save()

            # Perform restore
            result = self._perform_restore(backup, tables, dry_run)

            restore.records_restored = result["records_restored"]
            restore.tables_restored = result["tables_restored"]
            restore.status = "completed"
            restore.completed_at = timezone.now()
            restore.duration = restore.completed_at - restore.started_at

        except Exception as e:
            restore.status = "failed"
            restore.error_message = str(e)
            restore.completed_at = timezone.now()
            if restore.started_at:
                restore.duration = restore.completed_at - restore.started_at

        restore.save()
        return restore

    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Delete backups older than retention period"""
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        old_backups = Backup.objects.filter(created_at__lt=cutoff_date, status="completed")

        deleted_count = 0
        for backup in old_backups:
            if backup.file_path and os.path.exists(backup.file_path):
                try:
                    os.remove(backup.file_path)
                    deleted_count += 1
                except OSError:
                    pass  # File might already be deleted

        # Delete database records
        old_backups.delete()

        return deleted_count

    def _generate_backup_file(self, backup: Backup, tables: Optional[List[str]] = None) -> str:
        """Generate the actual backup file"""

        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{backup.name}_{timestamp}.json.gz"
        file_path = os.path.join(self.backup_dir, filename)

        # Get data from database
        data = {}
        tables_to_backup = tables or self._get_all_tables()

        with connection.cursor() as cursor:
            for table in tables_to_backup:
                if self._table_exists(table):
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()

                    # Convert to list of dicts
                    table_data = []
                    for row in rows:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            # Handle datetime serialization
                            if isinstance(row[i], datetime):
                                row_dict[col] = row[i].isoformat()
                            else:
                                row_dict[col] = row[i]
                        table_data.append(row_dict)

                    data[table] = table_data

        # Write to compressed JSON file
        with gzip.open(file_path, "wt", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path

    def _perform_restore(
        self, backup: Backup, tables: Optional[List[str]] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """Perform the actual restore operation"""

        if not backup.file_path or not os.path.exists(backup.file_path):
            raise ValueError("Backup file not found")

        # Read backup data
        with gzip.open(backup.file_path, "rt", encoding="utf-8") as f:
            data = json.load(f)

        tables_to_restore = tables or list(data.keys())
        records_restored = 0
        tables_restored = []

        with transaction.atomic():
            for table in tables_to_restore:
                if table in data and self._table_exists(table):
                    table_data = data[table]
                    if not dry_run:
                        # Clear existing data
                        with connection.cursor() as cursor:
                            cursor.execute(f"DELETE FROM {table}")

                        # Insert new data
                        if table_data:
                            with connection.cursor() as cursor:
                                for row in table_data:
                                    columns = list(row.keys())
                                    values = [row[col] for col in columns]
                                    placeholders = ", ".join(["%s"] * len(columns))
                                    columns_str = ", ".join(columns)

                                    sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                                    cursor.execute(sql, values)

                    records_restored += len(table_data)
                    tables_restored.append(table)

            if dry_run:
                # Rollback the transaction for dry run
                transaction.set_rollback(True)

        return {"records_restored": records_restored, "tables_restored": tables_restored}

    def _get_all_tables(self) -> List[str]:
        """Get all database tables"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                AND table_name NOT LIKE 'django_%'
                AND table_name NOT LIKE 'auth_%'
                ORDER BY table_name
            """)
            return [row[0] for row in cursor.fetchall()]

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
            """,
                [table_name],
            )
            return cursor.fetchone()[0]

    def _count_records(self, tables: Optional[List[str]] = None) -> int:
        """Count total records in specified tables"""
        tables_to_count = tables or self._get_all_tables()
        total_count = 0

        with connection.cursor() as cursor:
            for table in tables_to_count:
                if self._table_exists(table):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_count += cursor.fetchone()[0]

        return total_count

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        if not os.path.exists(file_path):
            return ""

        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)

        return hash_sha256.hexdigest()


class BackupScheduler:
    """Service for managing scheduled backups"""

    def __init__(self):
        self.backup_service = BackupService()

    def run_scheduled_backups(self) -> List[Backup]:
        """Run all due scheduled backups"""
        now = timezone.now()
        due_schedules = BackupSchedule.objects.filter(is_active=True, next_run__lte=now)

        completed_backups = []

        for schedule in due_schedules:
            try:
                # Create backup name
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                backup_name = f"{schedule.name}_{timestamp}"

                # Create backup
                backup = self.backup_service.create_backup(name=backup_name, backup_type=schedule.backup_type)

                if backup.is_successful:
                    completed_backups.append(backup)

                # Update schedule
                schedule.last_run = now
                schedule.calculate_next_run()
                schedule.save()

                # Cleanup old backups
                self.backup_service.cleanup_old_backups(schedule.retention_days)

            except Exception as e:
                # Log error but continue with other schedules
                print(f"Error running scheduled backup {schedule.name}: {e}")

        return completed_backups

    def create_schedule(
        self, name: str, frequency: str, backup_type: str = "full", user=None, **kwargs
    ) -> BackupSchedule:
        """Create a new backup schedule"""

        schedule = BackupSchedule.objects.create(
            name=name, frequency=frequency, backup_type=backup_type, created_by=user, **kwargs
        )

        # Calculate next run time
        schedule.calculate_next_run()
        schedule.save()

        return schedule
