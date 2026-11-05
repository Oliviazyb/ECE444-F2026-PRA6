"""Create the SQLite table for deployment without deleting existing posts."""

from project.app import app, get_db


if __name__ == "__main__":
    with app.app_context():
        database = get_db()
        database.execute(
            "CREATE TABLE IF NOT EXISTS entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, text TEXT NOT NULL)"
        )
        database.commit()
