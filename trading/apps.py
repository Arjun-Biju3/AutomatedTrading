from django.apps import AppConfig
import threading

class TradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trading'

    def ready(self):
        """ Start the scheduler when Django starts, ensuring it's only started once """
        from .scheduler import start_scheduler  # Import inside to avoid premature execution

        if not threading.main_thread().is_alive():
            return  # Prevent multiple starts in development mode
        
        start_scheduler()
