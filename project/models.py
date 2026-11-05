from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Post(db.Model):
    # Keep the existing table so this stage preserves local SQLite posts.
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Post {self.id}: {self.title}>"
