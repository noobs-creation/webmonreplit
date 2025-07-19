# app.py
# This Flask application provides a basic web interface for the monitoring system.
# The actual monitoring logic runs in monitor.py as an Always-on task.

import os
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# --- Configuration ---
# It's highly recommended to set these as environment variables on PythonAnywhere.
# For local testing, you can uncomment and set them here, but DO NOT commit sensitive info.
# app.config['WEBSITE_URL'] = os.environ.get('WEBSITE_URL', 'https://www.barodasuntechnologies.com')
# app.config['SENDER_EMAIL'] = os.environ.get('SENDER_EMAIL', 'barodasuntech@gmail.com')
# app.config['SENDER_PASSWORD'] = os.environ.get('SENDER_PASSWORD', 'Baroda@2025')
# app.config['RECEIVER_EMAIL'] = os.environ.get('RECEIVER_EMAIL', 'siddhanth.bob@gmail.com')

# Basic check to ensure essential environment variables are set
if not all(os.environ.get(var) for var in ['WEBSITE_URL', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECEIVER_EMAIL']):
    print("WARNING: Essential environment variables (WEBSITE_URL, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL) are not set.")
    print("Please set them on PythonAnywhere or in your local environment.")

# Simple in-memory status storage for the web app (monitor.py updates a file)
# In a real-world scenario, you might use a small database or file to share status.
# For this example, the web app just displays a static message or reads from a simple status file.

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
            <p>The core monitoring logic runs as an "Always-on task" on PythonAnywhere, separate from this web interface.</p>
            <p>Check your email for real-time alerts.</p>
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

if __name__ == '__main__':
    # For local development, run: python app.py
    # On PythonAnywhere, this will be handled by the WSGI file.
    app.run(debug=True)
