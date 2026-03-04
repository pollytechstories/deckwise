from flask import Flask, redirect, url_for
from sqlalchemy import text

from config import Config
from .extensions import db, login_manager, bcrypt, csrf
from .markdown_utils import render_markdown


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register Jinja2 filter
    app.jinja_env.filters["markdown"] = render_markdown

    # Register blueprints
    from .auth.routes import auth_bp
    from .decks.routes import decks_bp
    from .study.routes import study_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(decks_bp)
    app.register_blueprint(study_bp)

    @app.route("/")
    def index():
        return redirect(url_for("decks.dashboard"))

    # Create tables and set SQLite pragmas
    with app.app_context():
        from sqlalchemy import event

        @event.listens_for(db.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        db.create_all()

        # Migrate existing DBs: add suspended column if missing
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE cards ADD COLUMN suspended BOOLEAN DEFAULT 0 NOT NULL"))
                conn.commit()
            except Exception:
                pass  # Column already exists

    return app
