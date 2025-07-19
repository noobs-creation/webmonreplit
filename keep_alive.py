# keep_alive.py
# This script runs a small web server in a separate thread to keep the Replit Repl alive.

from flask import Flask
from threading import Thread

# Create a tiny Flask app just for the keep-alive server
app_keep_alive = Flask(__name__)

@app_keep_alive.route('/')
def home():
    """
    A simple route that responds to pings, indicating the server is alive.
    """
    return "I'm alive!"

def run_keep_alive():
    """
    Runs the keep-alive Flask app.
    It will listen on port 8080 (or another available port).
    """
    # Replit typically exposes port 8080 for web apps.
    # The host '0.0.0.0' makes the server accessible externally.
    app_keep_alive.run(host='0.0.0.0', port=8080)

def keep_alive():
    """
    Starts the keep-alive server in a new thread.
    This function should be called from your main application.
    """
    t = Thread(target=run_keep_alive)
    t.start()
