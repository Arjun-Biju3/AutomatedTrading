import random
import http.client
import smtplib
from email.message import EmailMessage
from datetime import datetime,timedelta
from django.http import HttpResponse
import random
import string

email_id = "ivpe68030@gmail.com"
app_password="utba gpfp sfgt lagn"


def generate_otp(length=6):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

def send_email(to,otp):
    msg=EmailMessage()
    subject="VERIFY PAN"
    body = f"Your OTP for PAN verification is {otp}. Use this OTP to validate your PAN. Do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user=email_id
    msg['from']=user
    password=app_password
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
     
def send_otp_chngpass(to,otp):
    msg=EmailMessage()
    subject="RESET PASSWORD"
    body=f"Your otp for changing password is {otp}.Please do not share it with any one.Keep it confidential"
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user=email_id
    msg['from']=user
    password=app_password
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
    
def send_status(to):
    msg=EmailMessage()
    subject="Voting"
    body=f"Congratulations you have successfully voted."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user=email_id
    msg['from']=user
    password=app_password
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
    


def validate_otp(request, otp):
    session_otp = request.session.get('otp')
    otp_expires_str = request.session.get('otp_expires')
    
    if session_otp and otp_expires_str:
        otp_expires = datetime.fromisoformat(otp_expires_str)
        
        if datetime.now() > otp_expires:
            return -1
    
        if str(session_otp) == otp:
            return 1
        else:
            return 0
    return None


def clear_otp(request):
    if 'otp' in request.session:
        del request.session['otp']
        del request.session['otp_expires']
    return HttpResponse("OTP cleared")


def send_mpin_email(to,otp):
    msg=EmailMessage()
    subject="Reset MPIN"
    body = f"Your OTP for changing MPIN is {otp}. Use this OTP to change your MPIN. Do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user=email_id
    msg['from']=user
    password=app_password
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
    
    
    
def send_password(to,password):
    msg=EmailMessage()
    subject="NEW PASSWORD"
    body = f"Your password is {password}. Use this password to login and change password once you loggedin. Do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user=email_id
    msg['from']=user
    password=app_password
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
    
    
    
def generate_random_password(length=10):
    """Generate a secure random password of specified length."""
    if length < 8:
        raise ValueError("Password length should be at least 8 characters for security.")

    # Define character pools
    uppercase_letters = string.ascii_uppercase  # A-Z
    lowercase_letters = string.ascii_lowercase  # a-z
    digits = string.digits  # 0-9
    special_characters = "!@#$%^&*()_-+=<>?/"

    # Ensure the password contains at least one of each type
    password_chars = [
        random.choice(uppercase_letters),
        random.choice(lowercase_letters),
        random.choice(digits),
        random.choice(special_characters),
    ]

    # Fill the rest of the password length with random choices
    all_characters = uppercase_letters + lowercase_letters + digits + special_characters
    password_chars += random.choices(all_characters, k=length - 4)

    # Shuffle to remove predictability and return as a string
    random.shuffle(password_chars)
    return "".join(password_chars)


