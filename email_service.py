import os
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_app(app):
    """Initialize the email service"""
    # Get email settings from environment variables
    sender_email = os.environ.get('MAIL_USERNAME', '')
    
    print("Direct SMTP email service initialized with:")
    print(f"SMTP Server: smtp.gmail.com")
    print(f"Sender Email: {sender_email}")
    print(f"Ready to send emails: {'Yes' if sender_email else 'No - missing configuration'}")

def send_health_notification(to_email, subject, html_content):
    """
    Send an email notification with health insights using direct SMTP
    
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject
        html_content (str): HTML content of the email
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get credentials from environment variables
        sender_email = os.environ.get('MAIL_USERNAME')
        sender_password = os.environ.get('MAIL_PASSWORD')
        
        # Remove any spaces from the app password (Google app passwords often have spaces for readability)
        if sender_password:
            sender_password = sender_password.replace(' ', '')
        
        if not sender_email or not sender_password:
            print("Error: Missing email credentials in environment variables")
            return False
        
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = f"Health Tracker <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        
        # Login to the server
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        
        # Close connection
        server.quit()
        
        print(f"\n==== EMAIL SENT SUCCESSFULLY ====\n")
        print(f"From: {sender_email}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"==== END EMAIL NOTIFICATION ====\n")
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
