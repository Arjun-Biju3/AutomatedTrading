from django.urls import path
from trading import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('logout/',views.logout_view,name='logout'),
    path('stocks/',views.stocks,name='stocks'),
    path('stock_details/<id>',views.stock_details,name='stock_details'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('add-funds/', views.add_funds, name='add_funds'),
    path('verify-identity/', views.verify_identity, name='verify_identity'),
    path('otp_varification/', views.varify_otp, name='verify_otp'),
    path('wallet/',views.wallet,name='wallet'),
    path('transactions/',views.transactions,name='transactions'),
    path('widhraw/',views.widhraw,name='widhraw'),
    path('profile/',views.profile,name='profile'),
    path('changeMpin',views.changeMpin,name='changeMpin'),
    path('addMpin/',views.addMpin,name='addMpin'),
    path('varify_mpin_otp',views.varify_mpin_otp,name='varify_mpin_otp'),
    path('addMpinAfterPan/',views.addMpinAfterPan,name='addMpinAfterPan'),
    path('change_password/',views.change_password,name='change_password'),
    path('verify_mpin/',views.verify_mpin,name='verify_mpin'),
    path('verify_mpin_buy/',views.verify_mpin_buy,name='verify_mpin_buy'),
    path('buy_stock/',views.buy_stock,name='buy_stock'),
    path('verify_mpin_sell/',views.verify_mpin_sell,name='verify_mpin_sell'),
    path('schedule_trade/<id>',views.schedule_trade,name='schedule_trade'),
    path('view_scheduled_trades/',views.view_scheduled_trades,name='view_scheduled_trades')
]
