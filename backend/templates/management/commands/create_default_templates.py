from django.core.management.base import BaseCommand
from templates.services import TemplateService


class Command(BaseCommand):
    help = 'Create default document templates'

    def handle(self, *args, **options):
        created_count = TemplateService.create_default_templates()

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} default document templates')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No new templates were created (they may already exist)')
            )