import os
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


from project.models import Post, db
from sqlalchemy.exc import SQLAlchemyError


def create_app(test_config=None):
    application = Flask(__name__)
    database = Path(__file__).resolve().parent.parent / "flaskr.db"
    database_url = os.getenv("DATABASE_URL") or f"sqlite:///{database}"
    # Render URLs use the PostgreSQL scheme; select our psycopg 3 driver.
    for prefix in ("postgres://", "postgresql://"):
        if database_url.startswith(prefix):
            database_url = "postgresql+psycopg://" + database_url[len(prefix) :]
            break
    application.config.update(
        DATABASE=database,
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        USERNAME=os.getenv("APP_USERNAME", "admin"),
        PASSWORD=os.getenv("APP_PASSWORD", "admin"),
        SECRET_KEY=os.getenv("SECRET_KEY", "development-only-change-before-deployment"),
    )
    if test_config:
        application.config.update(test_config)
    db.init_app(application)
    for rule, view, methods in (
        ("/", index, ["GET"]),
        ("/search/", search, ["GET"]),
        ("/login", login, ["GET", "POST"]),
        ("/logout", logout, ["GET"]),
        ("/add", add_entry, ["POST"]),
        ("/delete/<int:post_id>", delete_entry, ["GET"]),
    ):
        application.add_url_rule(rule, view_func=view, methods=methods)
    return application


def index():
    entries = (
        db.session.execute(db.select(Post).order_by(Post.id.desc())).scalars().all()
    )
    return render_template("index.html", entries=entries)


def search():
    query = request.args.get("query", "").strip()
    entries = []
    if query:
        posts = (
            db.session.execute(db.select(Post).order_by(Post.id.desc())).scalars().all()
        )
        keyword = query.casefold()
        entries = [
            post
            for post in posts
            if keyword in post.title.casefold() or keyword in post.text.casefold()
        ]
    return render_template("search.html", entries=entries, query=query)


def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != current_app.config["USERNAME"]:
            error = "Invalid username"
        elif request.form["password"] != current_app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("You were logged in")
            return redirect(url_for("index"))
    return render_template("login.html", error=error)


def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("index"))


def add_entry():
    if not session.get("logged_in"):
        abort(401)
    post = Post(title=request.form["title"], text=request.form["text"])
    db.session.add(post)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))


def login_required(view):
    """Only call the wrapped view when the client is authenticated."""

    @wraps(view)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify(status=0, message="Please log in."), 401
        return view(*args, **kwargs)

    return decorated_function


@login_required
def delete_entry(post_id):
    """Delete a post and return JSON for the browser's fetch request."""
    try:
        post = db.session.get(Post, post_id)
        if post is not None:
            db.session.delete(post)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(status=0, message="Could not delete post"), 500
    return jsonify(status=1, message="Post Deleted")


app = create_app()
