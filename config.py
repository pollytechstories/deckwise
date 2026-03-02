import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///deckwise.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB upload limit
