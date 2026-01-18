from app import create_app, db
import os

# This is what Gunicorn is looking for!
app = create_app()

if __name__ == "__main__":
    # This part only runs locally, not on Render
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)