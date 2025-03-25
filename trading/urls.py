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
    

]
