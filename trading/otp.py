import random
import http.client
import smtplib
from email.message import EmailMessage
from datetime import datetime,timedelta
from django.http import HttpResponse

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
    user="ivpe68030@gmail.com"
    msg['from']=user
    password="utba gpfp sfgt lagn"
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
     
def send_log_key(to,key):
    msg=EmailMessage()
    subject="Password"
    body=f"Your voting password is {key}.Please do not share it with any one.Keep it confidential"
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user="ivpe68030@gmail.com"
    msg['from']=user
    password="utba gpfp sfgt lagn"
     
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
    user="ivpe68030@gmail.com"
    msg['from']=user
    password="utba gpfp sfgt lagn"
     
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
    user="ivpe68030@gmail.com"
    msg['from']=user
    password="utba gpfp sfgt lagn"
     
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()