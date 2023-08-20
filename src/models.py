from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from random import choices
from string import ascii_letters, digits

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    bookmarks = db.relationship("Bookmark", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text(), nullable=True)
    url = db.Column(db.Text(), nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    visits = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_url()

    def generate_short_url(self):
        picked_chars = "".join(choices(ascii_letters + digits, k=3))

        link = self.query.filter_by(short_url=picked_chars).first()
        if link:
            return self.generate_short_url()
        return picked_chars

    def __repr__(self):
        return f"<Bookmark {self.url}>"
