from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from backup.services import BackupService

User = get_user_model()


class Command(BaseCommand):
    help = "Create a database backup"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name for the backup")
        parser.add_argument(
            "--type",
            type=str,
            choices=["full", "incremental", "manual", "scheduled"],
            default="manual",
            help="Type of backup (default: manual)",
        )
        parser.add_argument("--tables", type=str, help="Comma-separated list of tables to backup (default: all)")
        parser.add_argument("--user", type=str, help="Username of the user creating the backup")

    def handle(self, *args, **options):
        name = options["name"]
        backup_type = options["type"]
        tables = options.get("tables")
        username = options.get("user")

        # Parse tables
        if tables:
            tables = [t.strip() for t in tables.split(",")]

        # Get user
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')

        # Create backup
        service = BackupService()

        self.stdout.write(f"Creating {backup_type} backup: {name}")
        backup = service.create_backup(name=name, backup_type=backup_type, user=user, tables=tables)

        if backup.is_successful:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created backup "{name}"\n'
                    f"File: {backup.file_path}\n"
                    f"Size: {backup.file_size:,} bytes\n"
                    f"Records: {backup.record_count:,}\n"
                    f"Duration: {backup.duration}"
                )
            )
        else:
            raise CommandError(f"Backup failed: {backup.error_message}")
