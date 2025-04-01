import random
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now
from django.db import transaction
from .models import ScheduledTrade, Stock, Wallet, UserPortfolio, Trade

# Global scheduler instance
scheduler = BackgroundScheduler()

def execute_scheduled_trades():
    """ Executes scheduled trades if the time has arrived and updates their status """
    # Get all trades where scheduled_time is in the past and not yet executed
    scheduled_trades = ScheduledTrade.objects.filter(scheduled_time__lte=now(), executed=False)
    
    for trade in scheduled_trades:
        with transaction.atomic():
            stock = trade.stock
            balance = Wallet.objects.get(user=trade.user)
            
            # Perform Buy action
            if trade.action == 'BUY':
                if stock.current_price * trade.quantity <= balance.balance:
                    balance.balance -= stock.current_price * trade.quantity
                    stock.volume -= trade.quantity
                    balance.save()
                    stock.save()

                    # Check if stock is in user portfolio
                    portfolio_item, created = UserPortfolio.objects.get_or_create(
                        user=trade.user,
                        stock=stock,
                        defaults={'quantity': 0, 'buy_price': 0}
                    )
                    portfolio_item.quantity += trade.quantity
                    portfolio_item.buy_price += stock.current_price * trade.quantity
                    portfolio_item.save()

                    # Record the trade
                    Trade.objects.create(
                        user=trade.user,
                        stock=stock,
                        trade_type='BUY',
                        quantity=trade.quantity,
                        price=stock.current_price
                    )
            
            # Perform Sell action
            elif trade.action == 'SELL':
                portfolio_item = UserPortfolio.objects.get(user=trade.user, stock=stock)
                if portfolio_item.quantity >= trade.quantity:
                    portfolio_item.quantity -= trade.quantity
                    portfolio_item.save()

                    stock.volume += trade.quantity
                    balance.balance += stock.current_price * trade.quantity
                    stock.save()
                    balance.save()

                    # Record the trade
                    Trade.objects.create(
                        user=trade.user,
                        stock=stock,
                        trade_type='SELL',
                        quantity=trade.quantity,
                        price=stock.current_price
                    )

            # Mark the trade as executed
            trade.executed = True
            trade.save()

    print("✅ Scheduled trades executed successfully.")

def start_scheduler():
    """ Start the scheduler if not already running """
    if not scheduler.running:
        scheduler.add_job(execute_scheduled_trades, 'interval', minutes=1)
        scheduler.start()
        print("✅ Scheduler started successfully!")
