from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    percent_change = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)  
    last_updated = models.DateTimeField(auto_now=True)
    volume = models.IntegerField(default=50)
    market_cap=models.IntegerField(default=500)
    high_52 = models.IntegerField(default=500)
    low_52 = models.IntegerField(default=200)

    def __str__(self):
        return f"{self.symbol} - {self.name} ({self.percent_change}%)"

class Trade(models.Model):
    TRADE_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.trade_type} {self.quantity} {self.stock.symbol}"


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pan_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_setMpin = models.BooleanField(default=False)
    hashed_mpin = models.CharField(max_length=128, null=True, blank=True)  # Store hashed MPIN

    def set_mpin(self, raw_mpin):
        """Hashes and sets the MPIN"""
        self.hashed_mpin = make_password(raw_mpin)
        self.save()

    def verify_mpin(self, raw_mpin):
        """Checks if the provided MPIN matches the stored hash"""
        return check_password(raw_mpin, self.hashed_mpin)

    def __str__(self):
        return f"{self.user.username} - Verified: {self.is_verified}"
    
class UserPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    buy_price = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user}"
    
    

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)  # Store last 4 digits for security
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"



class ScheduledTrade(models.Model):
    ACTION_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField()
    scheduled_time = models.DateTimeField()
    buy_price = models.FloatField(default=0)
    executed = models.BooleanField(default=False)  # To check if the trade was executed

    def __str__(self):
        return f"{self.user} - {self.stock.symbol} - {self.action} at {self.scheduled_time}"
