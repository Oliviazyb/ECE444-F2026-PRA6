import os
import sqlite3
from pathlib import Path

from flask import (
    Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for,
)


app = Flask(__name__)
app.config["DATABASE"] = Path(__file__).resolve().parent.parent / "flaskr.db"
app.config.update(
    USERNAME=os.getenv("APP_USERNAME", "admin"),
    PASSWORD=os.getenv("APP_PASSWORD", "admin"),
    SECRET_KEY=os.getenv("SECRET_KEY", "development-only-change-before-deployment"),
)


def connect_db():
    """Open a connection whose rows support access by column name."""
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def get_db():
    """Reuse one connection within the current application context."""
    if "sqlite_db" not in g:
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    """Reset the database using schema.sql; existing entries are removed."""
    with app.app_context():
        database = get_db()
        with app.open_resource("schema.sql", mode="r") as schema:
            database.executescript(schema.read())
        database.commit()


@app.teardown_appcontext
def close_db(error):
    """Release the connection when the application context ends."""
    database = g.pop("sqlite_db", None)
    if database is not None:
        database.close()


@app.route("/")
def index():
    entries = get_db().execute("SELECT * FROM entries ORDER BY id DESC").fetchall()
    return render_template("index.html", entries=entries)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error = "Invalid username"
        elif request.form["password"] != app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("You were logged in")
            return redirect(url_for("index"))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("index"))


@app.route("/add", methods=["POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)
    database = get_db()
    database.execute(
        "INSERT INTO entries (title, text) VALUES (?, ?)",
        (request.form["title"], request.form["text"]),
    )
    database.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))


@app.route("/delete/<int:post_id>", methods=["GET"])
def delete_entry(post_id):
    """Delete a post and return JSON for the browser's fetch request."""
    database = get_db()
    try:
        database.execute("DELETE FROM entries WHERE id = ?", (post_id,))
        database.commit()
    except sqlite3.Error:
        database.rollback()
        return jsonify(status=0, message="Could not delete post"), 500
    return jsonify(status=1, message="Post Deleted")
