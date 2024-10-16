# main.py
from app import app, db

if __name__ == "__main__":
    with app.app_context():  # Push the app context
        db.create_all()  # Create tables based on models
    app.run(debug=True)
