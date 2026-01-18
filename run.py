from app import create_app

# Gunicorn will look for this 'app' variable
app = create_app()

if __name__ == "__main__":
    app.run()