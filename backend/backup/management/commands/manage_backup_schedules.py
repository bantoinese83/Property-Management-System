from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from backup.services import BackupScheduler

User = get_user_model()


class Command(BaseCommand):
    help = 'Manage backup schedules'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['create', 'list', 'delete', 'run'],
            help='Action to perform'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Schedule name (required for create, delete)'
        )
        parser.add_argument(
            '--frequency',
            type=str,
            choices=['hourly', 'daily', 'weekly', 'monthly'],
            help='Backup frequency (required for create)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['full', 'incremental', 'manual', 'scheduled'],
            default='full',
            help='Backup type (default: full)'
        )
        parser.add_argument(
            '--hour',
            type=int,
            help='Hour for daily/weekly/monthly backups (0-23)'
        )
        parser.add_argument(
            '--day-of-week',
            type=int,
            choices=range(7),
            help='Day of week for weekly backups (0=Monday, 6=Sunday)'
        )
        parser.add_argument(
            '--day-of-month',
            type=int,
            choices=range(1, 32),
            help='Day of month for monthly backups (1-31)'
        )
        parser.add_argument(
            '--retention',
            type=int,
            default=30,
            help='Retention period in days (default: 30)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username of the user creating the schedule'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'create':
            self._create_schedule(options)
        elif action == 'list':
            self._list_schedules()
        elif action == 'delete':
            self._delete_schedule(options)
        elif action == 'run':
            self._run_schedules()

    def _create_schedule(self, options):
        name = options.get('name')
        frequency = options.get('frequency')
        backup_type = options.get('type')
        hour = options.get('hour')
        day_of_week = options.get('day_of_week')
        day_of_month = options.get('day_of_month')
        retention = options.get('retention')
        username = options.get('user')

        if not name:
            raise CommandError('--name is required for create action')
        if not frequency:
            raise CommandError('--frequency is required for create action')

        # Get user
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')

        # Create schedule
        scheduler = BackupScheduler()
        schedule = scheduler.create_schedule(
            name=name,
            frequency=frequency,
            backup_type=backup_type,
            user=user,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            retention_days=retention
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Created backup schedule "{name}"\n'
                f'Frequency: {schedule.get_frequency_display()}\n'
                f'Type: {schedule.get_backup_type_display()}\n'
                f'Next run: {schedule.next_run}'
            )
        )

    def _list_schedules(self):
        from backup.models import BackupSchedule

        schedules = BackupSchedule.objects.all()

        if not schedules:
            self.stdout.write('No backup schedules found.')
            return

        self.stdout.write('Backup Schedules:')
        self.stdout.write('-' * 80)

        for schedule in schedules:
            status = 'Active' if schedule.is_active else 'Inactive'
            self.stdout.write(
                f'{schedule.name} ({schedule.get_frequency_display()})\n'
                f'  Status: {status}\n'
                f'  Type: {schedule.get_backup_type_display()}\n'
                f'  Next run: {schedule.next_run}\n'
                f'  Last run: {schedule.last_run or "Never"}\n'
            )

    def _delete_schedule(self, options):
        from backup.models import BackupSchedule

        name = options.get('name')
        if not name:
            raise CommandError('--name is required for delete action')

        try:
            schedule = BackupSchedule.objects.get(name=name)
            schedule.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted backup schedule "{name}"')
            )
        except BackupSchedule.DoesNotExist:
            raise CommandError(f'Backup schedule "{name}" not found')

    def _run_schedules(self):
        scheduler = BackupScheduler()
        backups = scheduler.run_scheduled_backups()

        if backups:
            self.stdout.write(
                self.style.SUCCESS(f'Created {len(backups)} scheduled backups')
            )
            for backup in backups:
                self.stdout.write(f'  - {backup.name}')
        else:
            self.stdout.write('No scheduled backups were due to run')