import sys
import os

# Add the current directory to path so it can find the 'app' package
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# This is exactly what Gunicorn needs
app = create_app()

if __name__ == "__main__":
    app.run()