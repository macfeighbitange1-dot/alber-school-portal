from app import create_app

# This is the variable Gunicorn is looking for
app = create_app()

if __name__ == "__main__":
    app.run()