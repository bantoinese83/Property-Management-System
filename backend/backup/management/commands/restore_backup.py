from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from backup.services import BackupService

User = get_user_model()


class Command(BaseCommand):
    help = "Restore from a database backup"

    def add_arguments(self, parser):
        parser.add_argument("backup_id", type=int, help="ID of the backup to restore from")
        parser.add_argument("--tables", type=str, help="Comma-separated list of tables to restore (default: all)")
        parser.add_argument("--user", type=str, help="Username of the user performing the restore")
        parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")

    def handle(self, *args, **options):
        backup_id = options["backup_id"]
        tables = options.get("tables")
        username = options.get("user")
        dry_run = options["dry_run"]

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

        # Restore backup
        service = BackupService()

        action = "Dry run restore" if dry_run else "Restoring"
        self.stdout.write(f"{action} from backup ID {backup_id}")

        if not dry_run:
            # Confirm destructive operation
            confirm = input("This will overwrite existing data. Continue? (yes/no): ")
            if confirm.lower() not in ["yes", "y"]:
                self.stdout.write("Restore cancelled.")
                return

        restore = service.restore_backup(backup_id=backup_id, user=user, tables=tables, dry_run=dry_run)

        if restore.status == "completed":
            action_word = "would be" if dry_run else "were"
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully {"simulated" if dry_run else "performed"} restore\n'
                    f"Records {action_word} restored: {restore.records_restored:,}\n"
                    f'Tables {action_word} restored: {", ".join(restore.tables_restored)}\n'
                    f"Duration: {restore.duration}"
                )
            )
        else:
            raise CommandError(f"Restore failed: {restore.error_message}")
