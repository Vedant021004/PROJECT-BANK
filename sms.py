import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import  load_dotenv
import os

load_dotenv()

def send_registration_alert(name, user_email ):
    """
    Sends a completely free expiration alert email directly to the supervisor.
    """
     
    sender_email = os.environ.get("SMTP_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD")  # Generated via Google Account security
     
    if not sender_email or not sender_password:
        print(f"[LOCAL DEV] Registration alert for {name} ({user_email}) recorded.")
        return True
     
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user_email
    message["Subject"] = f"  Registration Successful - INVENTRACK  "
    
    body = (
        f"Hello {name},\n\n"
        f"Registration at the INVENTRACK is successful.\n"
        f"Thankyou for registering and very congratulations for expanding your inventory with INVENTRACK.\n\n"
        f"Regards,\nTeam INVENTRACK"
         
    )
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        #  Connection to Gmail's free SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls() # Encrypt the connection
        server.login(sender_email, sender_password)
        
        server.sendmail(sender_email, user_email, message.as_string())
        server.quit()
        print(f"[Alert] Registration alert successfully routed to {user_email}")
        return True
        
    except Exception as e:
        print(f"[Warning] Email notification engine failed: {e}")
        return False

if __name__ == "__main__":
    send_free_expiry_alert()