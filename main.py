"""
R6 Siege Match Stats Analyzer - Main Entry Point
Executable launcher for the Flask application
"""

import os
import sys
import webbrowser
import threading
import time

# Determine if running as compiled executable
if getattr(sys, 'frozen', False):
    # Running as compiled - use the directory containing the exe
    BASE_DIR = os.path.dirname(sys.executable)
    # For PyInstaller, also check _MEIPASS for bundled files
    if hasattr(sys, '_MEIPASS'):
        BUNDLE_DIR = sys._MEIPASS
    else:
        BUNDLE_DIR = BASE_DIR
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

# Set environment variables for the app
os.environ['R6_ANALYST_BASE'] = BASE_DIR
os.environ['R6_ANALYST_BUNDLE'] = BUNDLE_DIR

# Add directories to path
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, BUNDLE_DIR)

# Change to base directory
os.chdir(BASE_DIR)

# Create necessary directories
data_dirs = ['data', 'data/uploads', 'data/match_data', 'data/reports']
for d in data_dirs:
    os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("=" * 60)
    print(" R6 Siege Match Stats Analyzer")
    print("=" * 60)
    print("")
    print(" L'interface web va s'ouvrir dans votre navigateur")
    print(" URL: http://localhost:5000")
    print("")
    print(" Fermez cette fenetre pour arreter l'application")
    print("=" * 60)
    print("")

    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Import and run Flask app
    from web.app import app

    # Run without debug mode for production
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
