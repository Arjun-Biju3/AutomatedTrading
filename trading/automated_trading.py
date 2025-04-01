import random
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.db import transaction
from decimal import Decimal  # Import Decimal from the decimal module
from .models import ScheduledTrade, Stock, Wallet, UserPortfolio, Trade
from datetime import datetime, timedelta
import pytz

# Global scheduler instance
scheduler = BackgroundScheduler()

def execute_scheduled_trades():
    """ Executes scheduled trades if the time has arrived and updates their status """
    current_time = timezone.now().astimezone(pytz.timezone('Asia/Kolkata'))  # ✅ Convert to India time
    print("Current Time:", current_time.strftime("%H:%M"))
    # Filter trades where only hour and minute match, ignoring the date
    scheduled_trades = ScheduledTrade.objects.filter(
        executed=False,
        scheduled_time__hour=current_time.hour,
        scheduled_time__minute=current_time.minute
    )
    print(scheduled_trades)
    for trade in scheduled_trades:
        with transaction.atomic():  # Wrap the trade logic in a transaction block
            stock = trade.stock
            balance = Wallet.objects.get(user=trade.user)
            
            # Perform Buy action
            if trade.action == 'BUY':
                if Decimal(stock.current_price) * Decimal(trade.quantity) <= Decimal(balance.balance):
                    balance.balance -= Decimal(stock.current_price) * Decimal(trade.quantity)
                    stock.volume -= trade.quantity
                    balance.save()
                    stock.save()

                    # Check if stock is in user portfolio
                    portfolio_item, created = UserPortfolio.objects.get_or_create(
                        user=trade.user,
                        stock=stock,
                        defaults={'quantity': 0, 'buy_price': Decimal(0)}  # Ensure buy_price is Decimal
                    )
                    portfolio_item.quantity += trade.quantity
                    portfolio_item.buy_price = Decimal(portfolio_item.buy_price) + Decimal(stock.current_price) * Decimal(trade.quantity)
                    portfolio_item.save()

                    # Record the trade
                    Trade.objects.create(
                        user=trade.user,
                        stock=stock,
                        trade_type='BUY',
                        quantity=trade.quantity,
                        price=Decimal(stock.current_price)  # Ensure price is Decimal
                    )
            
            # Perform Sell action
            elif trade.action == 'SELL':
                portfolio_item = UserPortfolio.objects.get(user=trade.user, stock=stock)
                if portfolio_item.quantity >= trade.quantity:
                    portfolio_item.quantity -= trade.quantity
                    portfolio_item.save()

                    stock.volume += trade.quantity
                    balance.balance += Decimal(stock.current_price) * Decimal(trade.quantity)
                    stock.save()
                    balance.save()

                    # Record the trade
                    Trade.objects.create(
                        user=trade.user,
                        stock=stock,
                        trade_type='SELL',
                        quantity=trade.quantity,
                        price=Decimal(stock.current_price)  # Ensure price is Decimal
                    )

            # Mark the trade as executed
            trade.buy_price="add current price of stock"
            trade.executed = True  # ✅ Ensuring executed items are marked as True
            trade.save()
    
    print("✅ Scheduled trades executed successfully.")

def start_automated_trading():
    """ Start the scheduler if not already running """
    if not scheduler.running:
        # Set the interval to 30 seconds
        scheduler.add_job(execute_scheduled_trades, 'interval', seconds=30)
        scheduler.start()
        print("✅ Trading Scheduler started successfully!")
