from datetime import datetime

from flask_login import UserMixin

from .extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    decks = db.relationship("Deck", backref="owner", cascade="all, delete-orphan")


class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    cards = db.relationship("Card", backref="deck", cascade="all, delete-orphan")


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=0)  # days
    repetitions = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    reviews = db.relationship("ReviewLog", backref="card", cascade="all, delete-orphan")


class ReviewLog(db.Model):
    __tablename__ = "review_log"

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    ease_factor_before = db.Column(db.Float, nullable=False)
    ease_factor_after = db.Column(db.Float, nullable=False)
    interval_before = db.Column(db.Integer, nullable=False)
    interval_after = db.Column(db.Integer, nullable=False)
    reviewed_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
