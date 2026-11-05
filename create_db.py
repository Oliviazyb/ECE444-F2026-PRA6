"""Create missing tables in the configured database without deleting posts."""

from project.app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
