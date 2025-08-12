from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self) -> None:
        # Import and initialize plugins when app is ready
        try:
            from .plugin_loader import initialize_plugins
            initialize_plugins()
        except Exception:
            # Avoid breaking startup on plugin errors; they can be reviewed in logs
            pass
