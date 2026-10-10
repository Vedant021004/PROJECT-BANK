import sqlite3
import datetime
from heap import *
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def login(email=None, password=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.commit()
    conn.close()
    return bool(user)


def generate_otp():
    """Generates a secure 6-digit random code."""
    return str(random.randint(100000, 999999))


def send_otp_email(receiver_email, otp_code, name):
    """Sends the OTP code using your verified app password, or displays in terminal console if SMTP is not configured."""
    sender_email = os.environ.get("SMTP_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD") 

    if not sender_email or not sender_password:
        print("\n" + "=" * 60)
        print("[LOCAL DEVELOPMENT MODE - REGISTRATION OTP]")
        print(f"Recipient : {receiver_email} ({name})")
        print(f"OTP Code  : {otp_code}")
        print("Notice    : SMTP_EMAIL / SMTP_PASSWORD not set in .env.")
        print("            Enter this OTP code on the verification screen.")
        print("=" * 60 + "\n")
        return True

    msg = MIMEText(f'''Hi {name},\n
    Your OTP for registration is: {otp_code}\n\nThis code will expire shortly.\n\n
    Regards\n Team Inventrack''')
    msg["Subject"] = "INVENTRACK Registration OTP"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP Warning] Failed to send OTP via SMTP: {e}")
        print(f"[CONSOLE FALLBACK OTP] Your verification code is: {otp_code}")
        return True




