from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError

from ..extensions import db, bcrypt
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("decks.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        # Validate
        errors = []
        try:
            valid = validate_email(email, check_deliverability=False)
            email = valid.normalized
        except EmailNotValidError:
            errors.append("Invalid email address.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/register.html", email=email), 400

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Welcome to DeckWise!", "success")
        return redirect(url_for("decks.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("decks.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get("next")
            flash("Logged in successfully.", "success")
            return redirect(next_page or url_for("decks.dashboard"))

        flash("Invalid email or password.", "error")
        return render_template("auth/login.html", email=email), 401

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
