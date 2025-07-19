# app.py
# This Flask application provides a basic web interface for the monitoring system.
# The actual monitoring logic runs in monitor.py as a separate process/thread.

import os
import subprocess
import sys
from flask import Flask, render_template_string, jsonify
from threading import Thread
import time

# Import the keep_alive function from our new file
from keep_alive import keep_alive

app = Flask(__name__)

# --- Configuration ---
# On Replit, you should set these as "Secrets" in the Repl's "Secrets" tab.
# For local testing, you can uncomment and set them here, but DO NOT commit sensitive info.
# app.config['WEBSITE_URL'] = os.environ.get('WEBSITE_URL', 'https://www.example.com')
# app.config['SENDER_EMAIL'] = os.environ.get('SENDER_EMAIL', 'your_sender_email@example.com')
# app.config['SENDER_PASSWORD'] = os.environ.get('SENDER_PASSWORD', 'your_email_app_password')
# app.config['RECEIVER_EMAIL'] = os.environ.get('RECEIVER_EMAIL', 'your_receiver_email@example.com')

# Basic check to ensure essential environment variables are set
# Replit's "Secrets" are accessed via os.environ
if not all(os.environ.get(var) for var in ['WEBSITE_URL', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECEIVER_EMAIL']):
    print("WARNING: Essential environment variables (WEBSITE_URL, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL) are not set.")
    print("Please set them as 'Secrets' in your Replit project.")

# HTML template for the main page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Monitor Status</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5;
        }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen bg-gray-100 p-4">
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <h1 class="text-3xl font-bold text-gray-800 mb-4">Website Monitoring System</h1>
        <p class="text-gray-600 mb-6">
            This system is actively monitoring <span class="font-semibold text-blue-600">{{ website_url }}</span>.
        </p>
        <p class="text-gray-700 text-lg mb-4">
            Status checks occur every 5 minutes.
        </p>
        <p class="text-gray-700 text-lg mb-6">
            If the website is down, an email alert will be sent to <span class="font-semibold text-green-600">{{ receiver_email }}</span> every 1 minute until it's back up.
        </p>
        <div class="bg-blue-50 border-l-4 border-blue-500 text-blue-700 p-4 rounded-md" role="alert">
            <p class="font-bold">Note:</p>
            <p>The core monitoring logic runs in the background within this Repl.</p>
            <p>This web interface helps keep the Repl active. Check your email for real-time alerts.</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """
    Renders the main page showing the monitoring system's purpose and configured URL/email.
    It reads the WEBSITE_URL and RECEIVER_EMAIL from environment variables.
    """
    website_url = os.environ.get('WEBSITE_URL', 'Not Configured')
    receiver_email = os.environ.get('RECEIVER_EMAIL', 'Not Configured')
    return render_template_string(HTML_TEMPLATE, website_url=website_url, receiver_email=receiver_email)

@app.route('/status')
def status():
    """
    Provides a simple JSON endpoint for system status (optional, for future expansion).
    Currently, it just indicates the monitoring is active.
    """
    return jsonify({"status": "monitoring_active", "message": "Check monitor.py logs for detailed status."})

def run_monitor_script():
    """
    Function to run the monitor.py script in a separate process.
    This ensures it runs continuously in the background.
    """
    print("Starting monitor.py in a separate process...")
    try:
        # Use sys.executable to ensure the correct Python interpreter is used
        # Use Popen to run it non-blocking
        subprocess.Popen([sys.executable, 'monitor.py'])
        print("monitor.py process started.")
    except Exception as e:
        print(f"Failed to start monitor.py: {e}")

if __name__ == '__main__':
    # Start the keep-alive server in a separate thread
    keep_alive()
    print("Keep-alive server started.")

    # Start the monitoring script in a separate process
    # Give the keep-alive server a moment to start up
    time.sleep(2)
    run_monitor_script()

    # Run the main Flask app
    # Replit automatically runs Flask apps on 0.0.0.0:8080
    app.run(host='0.0.0.0', port=8080)
