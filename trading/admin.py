from django.contrib import admin
from trading.models import *

admin.site.register(Wallet)
admin.site.register(UserProfile)
admin.site.register(Stock)
admin.site.register(UserPortfolio)
admin.site.register(Trade)
admin.site.register(Transaction)
admin.site.register(ScheduledTrade)
