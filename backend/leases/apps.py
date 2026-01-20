from django.apps import AppConfig


class LeasesConfig(AppConfig):
    name = "leases"

    def ready(self):
        import leases.signals
