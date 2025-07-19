# monitor.py
# This script is designed to run as an "Always-on task" on PythonAnywhere.
# It performs the actual website checks and sends email alerts.

import requests
import smtplib
import time
import os
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# --- Configuration ---
# Read configuration from environment variables.
# These MUST be set in your PythonAnywhere environment.
WEBSITE_URL = os.environ.get('WEBSITE_URL')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # Use an App Password for Gmail!
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

# Monitoring intervals
PING_INTERVAL_MINUTES = 5
EMAIL_INTERVAL_MINUTES = 1
WEBSITE_TIMEOUT_SECONDS = 10 # Timeout for website request

# --- Global State Variables ---
# These variables will maintain state across loop iterations.
is_website_down = False
last_ping_time = datetime.min # Initialize to a very old time to trigger immediate first ping
last_email_time = datetime.min # Initialize to a very old time to trigger immediate first email if down

# --- Helper Functions ---

def check_website_status(url):
    """
    Checks if the given website URL is reachable.
    Returns True if up, False if down.
    """
    try:
        # Send a GET request to the URL with a specified timeout
        response = requests.get(url, timeout=WEBSITE_TIMEOUT_SECONDS)
        # Check if the status code indicates success (200-299)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        # Catch any request-related errors (connection, timeout, HTTP errors)
        print(f"Website check failed for {url}: {e}")
        return False

def send_email(receiver_email, subject, body):
    """
    Sends an email using SMTP.
    Assumes Gmail SMTP server for simplicity. Adjust for other providers.
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email

        # Connect to Gmail's SMTP server (port 587 for TLS)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: # Use 465 for SSL, or 587 with starttls
            # server.starttls() # Uncomment if using port 587
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {receiver_email} with subject: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def main_monitor_loop():
    """
    The main loop that continuously monitors the website and sends alerts.
    This function should be called by the Always-on task.
    """
    global is_website_down, last_ping_time, last_email_time

    print("Website monitoring script started.")
    print(f"Monitoring: {WEBSITE_URL}")
    print(f"Alerts to: {RECEIVER_EMAIL}")

    # Validate configuration
    if not all([WEBSITE_URL, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
        print("ERROR: One or more required environment variables (WEBSITE_URL, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL) are not set.")
        print("Please configure them in your PythonAnywhere environment.")
        return # Exit if configuration is missing

    while True:
        current_time = datetime.now()

        # --- Website Ping Logic (every PING_INTERVAL_MINUTES) ---
        if current_time - last_ping_time >= timedelta(minutes=PING_INTERVAL_MINUTES):
            print(f"\n[{current_time}] Pinging {WEBSITE_URL}...")
            is_up = check_website_status(WEBSITE_URL)
            last_ping_time = current_time

            if is_up:
                if is_website_down:
                    # Website was down, now it's up. Send recovery email.
                    subject = f"✅ Website UP: {WEBSITE_URL}"
                    body = f"The website {WEBSITE_URL} is now back online at {current_time}."
                    print(f"Website is UP. Sending recovery email.")
                    send_email(RECEIVER_EMAIL, subject, body)
                    is_website_down = False # Reset status
                    last_email_time = datetime.min # Reset email timer for next down event
                else:
                    print(f"Website {WEBSITE_URL} is UP.")
            else:
                # Website is down
                if not is_website_down:
                    # First time detecting it's down
                    print(f"Website {WEBSITE_URL} is DOWN. Initiating alerts.")
                    is_website_down = True
                    # Trigger immediate first email
                    last_email_time = datetime.min # Make sure email sends immediately
                else:
                    print(f"Website {WEBSITE_URL} is STILL DOWN.")

        # --- Email Alert Logic (every EMAIL_INTERVAL_MINUTES, only if website is down) ---
        if is_website_down and (current_time - last_email_time >= timedelta(minutes=EMAIL_INTERVAL_MINUTES)):
            subject = f"🚨 Website DOWN: {WEBSITE_URL}"
            body = f"The website {WEBSITE_URL} is currently down. Last checked at {current_time}.\n\n" \
                   f"This alert will repeat every {EMAIL_INTERVAL_MINUTES} minute(s) until the website is back up."
            print(f"Website is down. Sending alert email.")
            if send_email(RECEIVER_EMAIL, subject, body):
                last_email_time = current_time # Update last email time only if sent successfully

        # Sleep for a short duration before the next check
        # This prevents the loop from consuming 100% CPU.
        # It also allows for more granular checks than the main ping interval.
        time.sleep(10) # Sleep for 10 seconds

if __name__ == '__main__':
    # When running this script directly (e.g., as an Always-on task)
    main_monitor_loop()
