from django.apps import AppConfig


class ZonesAppConfig(AppConfig):  # Changed from ZonesConfig to ZonesAppConfig
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zones_app'  # Changed from 'zones' to 'zones_app'
    verbose_name = 'Zones Sensibles'
    
    def ready(self):
        # Import signals if you have any
        # import zones_app.signals
        pass

