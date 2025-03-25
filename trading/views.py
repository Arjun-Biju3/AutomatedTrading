from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from trading.models import *
from trading.otp import *
import socket

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to home page after login
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")  # Redirect to login page after logout


def home(request):
    return render(request, 'index.html')


def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect("register")

        # Create and save user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login") 

    return render(request, "register.html")


def home_view(request):
    all_stock = Stock.objects.filter(volume__isnull=False).exclude(volume=0)
    stocks = Stock.objects.filter(volume__isnull=False).exclude(volume=0)[:12] 
    watch = Stock.objects.order_by('-id').filter(volume__isnull=False).exclude(volume=0)[:8]
    context={'stocks': stocks,'watchlist':watch,'all':all_stock}
    return render(request, 'home.html',context)

def stocks(request):
    all_stock = Stock.objects.filter(volume__isnull=False).exclude(volume=0)
    context={'stocks':all_stock}
    return render(request,'stocks.html',context)

def stock_details(request, id):
    if request.method == 'POST':
        id = request.POST.get('id')
        quantity = int(request.POST.get('quantity', 1))  # Ensure quantity is an integer
        balance = Wallet.objects.get(user=request.user)
        stock = Stock.objects.get(id=id)

        if stock.current_price * quantity <= balance.balance:
            balance.balance = balance.balance - (stock.current_price * quantity)
            balance.save()
            stock.volume = stock.volume-quantity
            stock.save()
            UserPortfolio.objects.create(user=request.user,stock=stock,quantity=quantity,buy_price=stock.current_price)
            return redirect('portfolio')
        else:
            print("not possible")
            messages.error(request, "Insufficient Balance")
        print(stock.name)

    details = Stock.objects.get(id=id)
    context = {'stock': details}
    return render(request, 'stock_details.html', context)




def portfolio(request):
    balance, _ = Wallet.objects.get_or_create(user=request.user)  
    stocks = UserPortfolio.objects.filter(user=request.user)  

    context = {
        'stocks': stocks if stocks.exists() else None,  
        'balance': balance.balance  
    }
    return render(request, 'portfolio.html', context)




def add_funds(request):
    if request.method == "POST":
        valid,_ = UserProfile.objects.get_or_create(user=request.user)
        if(not valid.is_verified):
            return redirect('verify_identity')
        else:
            amount = request.POST.get("amount")
            user_wallet= Wallet.objects.get(user=request.user)
            try:
                amount = float(amount)
                if amount > 0:
                    user_wallet.balance += amount
                    user_wallet.save()
                    messages.success(request, f"${amount} added to your wallet!")
                    return redirect("portfolio")  # Redirect to portfolio page
                else:
                    messages.error(request, "Invalid amount entered.")
            except ValueError:
                messages.error(request, "Invalid input.")

    return render(request, "add_funds.html")


def verify_identity(request):
    messages.warning(request, "You are not verified. Verify PAN!")

    if request.method == "POST":
        email = request.user.email
        pan_number = request.POST.get("pan_number", "").strip().upper()
        phone_number = request.POST.get("phone_number", "").strip()
        request.session['pan_number'] = pan_number
        request.session['phone_number'] = phone_number
        otp = generate_otp()
        request.session['otp'] = otp
        request.session['otp_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
        request.session.modified = True  # Ensure session updates
        request.session.save()  # Force save session

        try:
            send_email(email, otp)
            return redirect('verify_otp')  # Ensure correct URL name
        except socket.gaierror as e:
            print(f"Socket error: {e}")  # Debugging
            messages.error(request, "Please check your internet connection.")

    return render(request, "verify_identity.html")


def varify_otp(request):
    success_message="OTP has been send succesfully"
    messages.success(request,success_message)
    if request.POST:
        otp=request.POST.get('otp')
        res=validate_otp(request,otp)
        if res==1:
            clear_otp(request)
            pan=request.session.get('pan_number')
            phone=request.session.get('phone_number')
            profile=UserProfile.objects.get(user=request.user)
            profile.pan_number=pan
            profile.phone_number=phone
            profile.is_verified=True
            profile.save()
            return redirect('add_funds')
        if res==-1:
            error_message="OTP Expired"
            messages.error(request,error_message)
        if res==0:
            error_message="Invalid OTP"
            messages.error(request,error_message)
       #resend
    if request.POST and 'resend' in request.POST:
        otp=generate_otp()
        email=request.user.email
        request.session['otp']=otp
        request.session['otp_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
        print(otp)
        send_email(email,otp)
        messages.success(request,"OTP has been send succesfully")

    return render(request,'otp.html')