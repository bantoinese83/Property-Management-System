from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Backup(models.Model):
    """Model to track database backups"""

    BACKUP_TYPES = (
        ('full', 'Full Database Backup'),
        ('incremental', 'Incremental Backup'),
        ('manual', 'Manual Backup'),
        ('scheduled', 'Scheduled Backup'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    name = models.CharField(max_length=255, unique=True)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # File storage
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=128, blank=True, help_text='SHA-256 checksum')

    # Metadata
    tables_included = models.JSONField(default=list, help_text='List of tables included in backup')
    record_count = models.PositiveIntegerField(default=0, help_text='Total records backed up')

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_backups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['backup_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_backup_type_display()})"

    @property
    def is_successful(self):
        return self.status == 'completed' and self.file_path

    @property
    def duration_seconds(self):
        """Duration in seconds"""
        if self.duration:
            return self.duration.total_seconds()
        return None


class BackupSchedule(models.Model):
    """Model for scheduling automated backups"""

    FREQUENCY_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    name = models.CharField(max_length=255, unique=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)

    # Schedule configuration
    hour = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Hour (0-23) for daily/weekly/monthly backups'
    )
    day_of_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Day of week (0=Monday, 6=Sunday) for weekly backups'
    )
    day_of_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Day of month (1-31) for monthly backups'
    )

    # Backup configuration
    backup_type = models.CharField(max_length=20, choices=Backup.BACKUP_TYPES, default='full')
    retention_days = models.PositiveIntegerField(
        default=30,
        help_text='Number of days to keep backups'
    )

    # Last run info
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='backup_schedules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

    def calculate_next_run(self):
        """Calculate when this schedule should run next"""
        from datetime import datetime, timedelta
        from django.utils import timezone

        now = timezone.now()

        if self.frequency == 'hourly':
            # Next hour
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        elif self.frequency == 'daily':
            # Tomorrow at specified hour
            next_run = (now + timedelta(days=1)).replace(hour=self.hour or 2, minute=0, second=0, microsecond=0)

        elif self.frequency == 'weekly':
            # Next occurrence of specified day at specified hour
            days_ahead = (self.day_of_week - now.weekday()) % 7
            if days_ahead == 0 and (now.hour >= (self.hour or 2)):
                days_ahead = 7
            next_run = (now + timedelta(days=days_ahead)).replace(hour=self.hour or 2, minute=0, second=0, microsecond=0)

        elif self.frequency == 'monthly':
            # Next month on specified day at specified hour
            if now.day >= (self.day_of_month or 1):
                # Next month
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=self.day_of_month or 1)
                else:
                    next_run = now.replace(month=now.month + 1, day=self.day_of_month or 1)
            else:
                # This month
                next_run = now.replace(day=self.day_of_month or 1)
            next_run = next_run.replace(hour=self.hour or 2, minute=0, second=0, microsecond=0)

        else:
            return None

        self.next_run = next_run
        return next_run


class BackupRestore(models.Model):
    """Model to track backup restoration operations"""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('rolled_back', 'Rolled Back'),
    )

    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='restores')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Restore configuration
    tables_to_restore = models.JSONField(default=list, help_text='Specific tables to restore, empty means all')
    dry_run = models.BooleanField(default=False, help_text='Test run without making changes')

    # Results
    records_restored = models.PositiveIntegerField(default=0)
    tables_restored = models.JSONField(default=list)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    # Error handling
    error_message = models.TextField(blank=True)

    # Rollback support
    can_rollback = models.BooleanField(default=False)
    rollback_backup = models.OneToOneField(
        Backup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rollback_for'
    )

    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='backup_restores'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Restore of {self.backup.name} ({self.get_status_display()})"