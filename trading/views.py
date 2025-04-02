from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from trading.models import *
from trading.otp import *
import socket
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from decimal import Decimal

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
        Wallet.objects.create(user=user)
        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login") 

    return render(request, "register.html")


@login_required(login_url='login')  
def home_view(request):
    token=request.session.get("h_token")
    all_stock = Stock.objects.filter(volume__isnull=False).exclude(volume=0)
    stocks = Stock.objects.filter(volume__isnull=False).exclude(volume=0)[:12] 
    watch = Stock.objects.order_by('-id').filter(volume__isnull=False).exclude(volume=0)[:8]
    context={'stocks': stocks,'watchlist':watch,'all':all_stock,"token":token}   
    return render(request, 'home.html',context)


@login_required(login_url='login')  
def stocks(request):
    all_stock = Stock.objects.filter(volume__isnull=False).exclude(volume=0)
    context={'stocks':all_stock}
    return render(request,'stocks.html',context)


def count_quantity(item):
    count = 0
    for i in item:
        count += i.quantity
    return count


@login_required(login_url='login')  
def stock_details(request, id):
    d_token=False
    if request.POST and "schedule" in request.POST:
        id = request.POST.get("id")
        return redirect('schedule_trade', id=id)
    if request.POST and "sell" in request.POST:
        item=UserPortfolio.objects.filter(user=request.user,stock__id=id)
        quantity = int(request.POST.get("quantity"))
        available_quantity = count_quantity(item)
        if item:
            if quantity > available_quantity:
                d_token=True
                messages.error(request,"You dont have such an amount of stock. Check quantity")
            else:
                request.session["sell_id"] = id
                request.session["sell_quantity"] = quantity
                return redirect('verify_mpin_sell')
        else:
            d_token=True
            messages.error(request,"You are not able to sell it. Buy it first")
        print(available_quantity)
    if request.method == 'POST' and "buy" in request.POST:
        id = int(request.POST.get('id'))
        quantity = int(request.POST.get('quantity', 1)) 
        balance = Wallet.objects.get(user=request.user)
        stock = Stock.objects.get(id=id)
        
        if stock.current_price * quantity <= balance.balance:
            request.session["stock_id"] = id
            request.session["quantity"] = quantity
            return redirect('verify_mpin_buy')
        else:
            print("not possible")
            d_token=True
            messages.error(request, "Insufficient Balance")
        print(stock.name)

    details = Stock.objects.get(id=id)
    context = {'stock': details,"token":d_token}
    return render(request, 'stock_details.html', context)



@login_required(login_url='login')  
def portfolio(request):
    if request.POST:
        id = request.POST.get("id")
        request.session["sell_id"] = id
        return redirect('')
    balance, _ = Wallet.objects.get_or_create(user=request.user)  
    stocks = UserPortfolio.objects.filter(user=request.user)  

    context = {
        'stocks': stocks if stocks.exists() else None,  
        'balance': balance.balance  
    }
    return render(request, 'portfolio.html', context)



@login_required(login_url='login')  
def add_funds(request):
    if request.method == "POST":
        valid,_ = UserProfile.objects.get_or_create(user=request.user)
        if(not valid.is_verified):
            return redirect('verify_identity')
        else:
            amount = request.POST.get("amount")
            card_number= request.POST.get("card_number")
            user_wallet= Wallet.objects.get(user=request.user)
            try:
                amount = float(amount)
                if amount > 0:
                    user_wallet.balance += amount
                    user_wallet.save()
                    Transaction.objects.create(user=request.user,card_number=card_number,amount=amount,transaction_type="DEPOSIT")
                    messages.success(request, f"${amount} added to your wallet!")
                    return redirect("wallet")  # Redirect to portfolio page
                else:
                    pass
                    # messages.error(request, "Invalid amount entered.")
            except ValueError:
                pass
                # messages.error(request, "Invalid input.")

    return render(request, "add_funds.html")


@login_required(login_url='login')  
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


@login_required(login_url='login')  
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
            profile,_=UserProfile.objects.get_or_create(user=request.user)
            profile.pan_number=pan
            profile.phone_number=phone
            profile.is_verified=True
            profile.save()
            if not profile.is_setMpin:
                return redirect('addMpinAfterPan')
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


@login_required(login_url='login')  
def wallet(request):
    balance = Wallet.objects.get(user=request.user)
    return render(request,'wallet.html',{'balance':balance})


@login_required(login_url='login')  
def transactions(request):
    transactions=Transaction.objects.filter(user=request.user)
    context={"transactions":transactions}
    return render(request,'transaction.html',context)


@login_required(login_url='login')  
def widhraw(request):
    wallet = Wallet.objects.get(user=request.user)
    context = {"wallet":wallet}
    if request.POST:
        amount = float(request.POST.get("amount", 0))
        account_number = request.POST.get("account_number")
        balance = Wallet.objects.get(user=request.user)
        if amount < 100:
            messages.error(request, "Minimum amount to be widhrawn is 100.")
        elif amount > balance.balance:
            messages.error(request, "Insufficient balance.")
        elif not account_number:
            messages.error(request, "Enter a valid account number.")
        else:
            request.session["amount"] = amount
            request.session["account_number"] = account_number
            return redirect('verify_mpin')
    return render(request,'widhraw.html',context)



@login_required(login_url='login')  
def profile(request):
    userProfile,_ = UserProfile.objects.get_or_create(user=request.user)
    wallet,_= Wallet.objects.get_or_create(user=request.user)  # Get wallet balance
    context = {'user': request.user, 'wallet': wallet,"userprofile":userProfile}
    return render(request, 'profile.html', context)



@login_required(login_url='login')  
def varify_mpin_otp(request):
    if request.POST:
        otp=request.POST.get('otp')
        res=validate_otp(request,otp)
        if res==1:
            clear_otp(request)
            pin = request.session.get("new_mpin")
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.set_mpin(pin)
            request.session.pop("new_mpin", None)
            messages.success(request,"MPIN changed successfully")
            return redirect('profile')
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
        send_mpin_email(email,otp)
        messages.success(request,"OTP has been send succesfully")

    return render(request,'otp.html')




@login_required(login_url='login')  
def changeMpin(request):
    status = UserProfile.objects.get(user=request.user)
    if not status.is_setMpin:
        return redirect('addMpin')
    if request.POST:
        new_mpin = request.POST.get("new_mpin")
        confirm_mpin = request.POST.get("confirm_mpin")
        if new_mpin and confirm_mpin and new_mpin == confirm_mpin:
            request.session["new_mpin"] = new_mpin
            otp = generate_otp()
            request.session['otp']=otp
            request.session['otp_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
            send_mpin_email(request.user.email,otp)
            return redirect('varify_mpin_otp')
        else:
            messages.error(request, 'MPINs do not match. Please try again.')
    return render(request,'changeMpin.html')


@login_required(login_url='login')  
def addMpin(request):
    if request.method == 'POST':
        new_mpin = request.POST.get('new_mpin')
        confirm_mpin = request.POST.get('confirm_mpin')

        if new_mpin and confirm_mpin and new_mpin == confirm_mpin:
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.set_mpin(new_mpin)
            userprofile.is_setMpin=True
            userprofile.save()
            messages.success(request, 'MPIN set successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'MPINs do not match. Please try again.')
    return render(request,'add_mpin.html')



@login_required(login_url='login')  
def addMpinAfterPan(request):
    if request.method == 'POST':
        new_mpin = request.POST.get('new_mpin')
        confirm_mpin = request.POST.get('confirm_mpin')

        if new_mpin and confirm_mpin and new_mpin == confirm_mpin:
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.set_mpin(new_mpin)
            userprofile.is_setMpin=True
            userprofile.save()
            messages.success(request, 'MPIN set successfully!')
            return redirect('add_funds')
        else:
            messages.error(request, 'MPINs do not match. Please try again.')
    return render(request,'add_mpin.html')




@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match.")
        elif len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  
            messages.success(request, "Password changed successfully!")
            return redirect('profile')

    return render(request, 'change_password.html')


def verify_mpin(request):
    if request.method == "POST":
        entered_mpin = request.POST.get("mpin")
        print(entered_mpin)
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.verify_mpin(entered_mpin):
            balance = Wallet.objects.get(user=request.user)
            amount = request.session.get("amount")
            account_number = request.session.get("account_number")
            balance.balance = balance.balance-amount
            balance.save()
            Transaction.objects.create(user=request.user,card_number=account_number,amount=amount,transaction_type="WITHDRAWAL")
            request.session.pop("amount", None)
            request.session.pop("account_number", None)
            return redirect('wallet')
           
        else:
            messages.error(request, "Invalid MPIN. Please try again.")

    return render(request, 'verify_mpin.html')


from decimal import Decimal

def verify_mpin_buy(request):
    if request.method == "POST":
        entered_mpin = request.POST.get("mpin")
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.verify_mpin(entered_mpin):
            id = request.session.get("stock_id")
            quantity = int(request.session.get("quantity"))
            balance = Wallet.objects.get(user=request.user)
            stock = Stock.objects.get(id=id)
            
            # Convert balance.balance to Decimal before performing subtraction
            balance.balance = Decimal(balance.balance) - Decimal(stock.current_price) * Decimal(quantity)
            balance.save()
            
            stock.volume = stock.volume - quantity
            stock.save()

            item = UserPortfolio.objects.filter(user=request.user, stock__id=id)
            if item:
                for i in item:
                    i.quantity += quantity
                    i.buy_price += float(stock.current_price) * quantity
                    i.save()
            else:
                price = stock.current_price * quantity
                UserPortfolio.objects.create(user=request.user, stock=stock, quantity=quantity, buy_price=price)

            Trade.objects.create(
                user=request.user,
                stock=stock,
                trade_type="BUY",
                quantity=quantity,
                price=stock.current_price
            )
            request.session.pop("stock_id", None)
            request.session.pop("quantity", None)
            return redirect('portfolio')
           
        else:
            messages.error(request, "Invalid MPIN. Please try again.")

    return render(request, 'verify_mpin.html')


def buy_stock(request):
    request.session["h_token"] = False
    if request.POST and "buy" in  request.POST:
        id = request.POST.get('stock')
        quantity = int(request.POST.get('quantity', 1))  # Ensure quantity is an integer
        balance = Wallet.objects.get(user=request.user)
        stock = Stock.objects.get(id=id)

        if stock.current_price * quantity <= balance.balance:
            request.session["stock_id"] = id
            request.session["quantity"] = quantity
            return redirect('verify_mpin_buy')
        else:
            print("not possible")
            request.session["h_token"] = True
            messages.error(request, "Insufficient Balance")
    if request.POST and "schedule" in request.POST:
        id = request.POST.get('stock')
        return redirect('schedule_trade',id=id)
    
    return redirect('home')




def verify_mpin_sell(request):
    if request.method == "POST":
        entered_mpin = request.POST.get("mpin")
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.verify_mpin(entered_mpin):
            id = request.session.get("sell_id")
            quantity = int(request.session.get("sell_quantity"))  # Make sure quantity is an integer
            item = UserPortfolio.objects.get(user=request.user, stock__id=id)
            new_quantity = item.quantity - quantity
            stock = Stock.objects.get(id=item.stock.id)
            
            # Handle the case where the item quantity becomes zero
            if new_quantity == 0:
                item.delete()
                stock.volume += quantity
                balance = Wallet.objects.get(user=request.user)
                balance.balance = Decimal(balance.balance) + Decimal(stock.current_price) * Decimal(quantity)  # Convert balance.balance and stock.current_price to Decimal
                balance.save()
                stock.save()
                Trade.objects.create(
                    user=request.user,
                    stock=stock,
                    trade_type="SELL",
                    quantity=quantity,
                    price=stock.current_price
                )
                request.session.pop("sell_id", None)
                return redirect('portfolio')
            else:
                item.quantity = new_quantity
                stock.volume += quantity
                balance = Wallet.objects.get(user=request.user)
                balance.balance = Decimal(balance.balance) + Decimal(stock.current_price) * Decimal(quantity)  # Convert balance.balance and stock.current_price to Decimal
                balance.save()
                stock.save()
                item.save()
                Trade.objects.create(
                    user=request.user,
                    stock=stock,
                    trade_type="SELL",
                    quantity=quantity,
                    price=stock.current_price
                )
                request.session.pop("sell_id", None)
                return redirect('portfolio')
        else:
            messages.error(request, "Invalid MPIN. Please try again.")

    return render(request, 'verify_mpin.html')




def verify_mpin_schedule(request):
    if request.method == "POST":
        entered_mpin = request.POST.get("mpin")
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return redirect('verify_identity')
        

        if user_profile.verify_mpin(entered_mpin):
            id = request.session.get("schedule_id")
            quantity = int(request.session.get("schedule_quantity"))  # Make sure quantity is an integer
            action =request.session.get("action")
            scheduled_time = request.session.get("scheduled_time")
            stock = Stock.objects.get(id=id)
            print(id,quantity,action,scheduled_time,stock.name)
            try:
                quantity = int(quantity)
                scheduled_time = timezone.datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
            except ValueError:
                messages.error(request, "Invalid input format.")
                return redirect("schedule_trade", id=id)

            # Save the scheduled trade
            ScheduledTrade.objects.create(
                user=request.user,
                stock=stock,
                action=action,
                quantity=quantity,
                scheduled_time=scheduled_time,
            )
            request.session.pop("sell_id", None)
            return redirect("view_scheduled_trades")
        else:
            messages.error(request, "Invalid MPIN. Please try again.")

    return render(request, 'verify_mpin.html')




@login_required(login_url='login')
def schedule_trade(request, id):
    quantity_item = 0
    display=False
    stock = Stock.objects.get(id=id)  # Get stock details
    item = UserPortfolio.objects.filter(user=request.user, stock__id=id).first()
    if item:
        if item.quantity > 0:
            display = True
            quantity_item = item.quantity
        else:
            display = False
    if request.method == "POST":
        action = request.POST.get("action")  # Buy or Sell
        quantity = request.POST.get("quantity")
        scheduled_time = request.POST.get("scheduled_time")

        # Validate the input
        if not action or not quantity or not scheduled_time:
            messages.error(request, "All fields are required.")
            return redirect("schedule_trade", id=id)
        else:
            request.session["schedule_id"] = id
            request.session["action"] = action
            request.session["schedule_quantity"] = quantity
            request.session["scheduled_time"] = scheduled_time
            return redirect('verify_mpin_schedule')
    return render(request, "schedule_trade.html", {"stock": stock,"display":display,"quantity":quantity_item})


@login_required(login_url="login")
def view_scheduled_trades(request):
    trades = ScheduledTrade.objects.filter(user=request.user).order_by("scheduled_time")
    return render(request, "view_scheduled_trades.html", {"trades": trades})

def forgot_password(request):
    if request.POST:
        otp=request.POST.get('otp')
        email = request.session.get("reset_password_email")
        res=validate_otp(request,otp)
        if res==1:
            clear_otp(request)
            new_password = generate_random_password()
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            send_password(email,new_password)
            messages.success(request,"Check your mail for new password")
            return redirect('login')
        if res==-1:
            error_message="OTP Expired"
            messages.error(request,error_message)
        if res==0:
            error_message="Invalid OTP"
            messages.error(request,error_message)
        if request.POST and 'resend' in request.POST:
            otp=generate_otp()
            request.session['otp']=otp
            request.session['otp_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
            send_otp_chngpass(email,otp)
            messages.success(request,"OTP has been send succesfully")
    return render(request,'otp.html')


def request_password_reset(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            otp = generate_otp()
            request.session['otp']=otp
            request.session["reset_password_email"] = email
            request.session['otp_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
            send_otp_chngpass(email,otp)
            messages.success(request, "A reset link has been sent to your email.")
            return redirect("forgot_password")  
        else:
            messages.error(request, "No account found with that email.")

    return render(request, "forgot_password.html")

@login_required(login_url="login")
def trading_history(request):
    trades = Trade.objects.filter(user=request.user).order_by("-timestamp")  # Show latest first
    return render(request, "trading_history.html", {"trades": trades})