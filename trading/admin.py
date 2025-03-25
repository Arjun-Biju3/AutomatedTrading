from django.contrib import admin
from trading.models import Wallet,UserProfile,Stock,UserPortfolio

admin.site.register(Wallet)
admin.site.register(UserProfile)
admin.site.register(Stock)
admin.site.register(UserPortfolio)
