import random
import logging
from decimal import Decimal  # Import Decimal to handle precise calculations
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now
from django.db import connections
from django.db.utils import OperationalError
from .models import Stock

# Logger to track scheduler status
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()

def update_stock_prices():
    """ Update stock prices randomly """
    try:
        # Check if DB is ready before querying
        connection = connections['default']
        connection.ensure_connection()

        stocks = Stock.objects.all()
        for stock in stocks:
            # Convert percent change to Decimal
            percent_change = Decimal(round(random.uniform(-5, 5), 2))
            # Calculate new price using Decimal for precision
            multiplier = Decimal(1) + (percent_change / Decimal(100))
            new_price = (stock.current_price * multiplier).quantize(Decimal("0.01"))  # Ensure Decimal precision

            # Prevent negative prices
            stock.percent_change = percent_change
            stock.current_price = max(Decimal("1.00"), new_price)
            stock.last_updated = now()
            stock.save()
        
        logger.info("✅ Stock prices updated successfully!")

    except OperationalError:
        logger.error("❌ Database not ready, skipping stock price update.")

def start_scheduler():
    """ Start the scheduler if not already running """
    if not scheduler.running:
        scheduler.add_job(update_stock_prices, 'interval', minutes=1)
        scheduler.start()
        logger.info("✅ Scheduler started successfully!")
