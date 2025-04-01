from django.apps import AppConfig
import threading

class TradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trading'

    def ready(self):
        """ Start both schedulers when Django starts, ensuring they are only started once """
        from .scheduler import start_scheduler  # For stock price update scheduler
        from .automated_trading import start_automated_trading  # For automated trading scheduler

        if not threading.main_thread().is_alive():
            return  # Prevent multiple starts in development mode

        start_scheduler()  # Start the stock price update scheduler
        start_automated_trading()  # Start the automated trading scheduler
