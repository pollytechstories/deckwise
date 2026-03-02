import json

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models import Deck, Card

decks_bp = Blueprint("decks", __name__, url_prefix="/decks")


def get_deck_or_404(deck_id):
    deck = db.session.get(Deck, deck_id)
    if not deck or deck.user_id != current_user.id:
        abort(404)
    return deck


@decks_bp.route("/")
@login_required
def dashboard():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.created_at.desc()).all()
    now = datetime.utcnow()
    deck_stats = []
    for deck in decks:
        total = len(deck.cards)
        due = sum(1 for c in deck.cards if c.next_review and c.next_review <= now)
        deck_stats.append({"deck": deck, "total": total, "due": due})
    return render_template("decks/dashboard.html", deck_stats=deck_stats)


@decks_bp.route("/new", methods=["POST"])
@login_required
def new_deck():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Deck name is required.", "error")
        return redirect(url_for("decks.dashboard"))

    deck = Deck(name=name, user_id=current_user.id)
    db.session.add(deck)
    db.session.commit()

    if request.headers.get("HX-Request"):
        # Return updated deck list
        return redirect(url_for("decks.dashboard"))

    flash("Deck created.", "success")
    return redirect(url_for("decks.dashboard"))


@decks_bp.route("/<int:deck_id>/rename", methods=["POST"])
@login_required
def rename_deck(deck_id):
    deck = get_deck_or_404(deck_id)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Deck name is required.", "error")
        return redirect(url_for("decks.dashboard"))

    deck.name = name
    db.session.commit()

    if request.headers.get("HX-Request"):
        return redirect(url_for("decks.dashboard"))

    flash("Deck renamed.", "success")
    return redirect(url_for("decks.dashboard"))


@decks_bp.route("/<int:deck_id>/delete", methods=["POST"])
@login_required
def delete_deck(deck_id):
    deck = get_deck_or_404(deck_id)
    db.session.delete(deck)
    db.session.commit()

    if request.headers.get("HX-Request"):
        return redirect(url_for("decks.dashboard"))

    flash("Deck deleted.", "success")
    return redirect(url_for("decks.dashboard"))


@decks_bp.route("/<int:deck_id>")
@login_required
def view_deck(deck_id):
    deck = get_deck_or_404(deck_id)
    cards = Card.query.filter_by(deck_id=deck.id).order_by(Card.created_at.desc()).all()
    now = datetime.utcnow()
    due_count = sum(1 for c in cards if c.next_review and c.next_review <= now)
    return render_template("decks/view.html", deck=deck, cards=cards, due_count=due_count)


@decks_bp.route("/<int:deck_id>/cards/new", methods=["POST"])
@login_required
def new_card(deck_id):
    deck = get_deck_or_404(deck_id)
    front = request.form.get("front", "").strip()
    back = request.form.get("back", "").strip()

    if not front or not back:
        flash("Both front and back are required.", "error")
        return redirect(url_for("decks.view_deck", deck_id=deck.id))

    card = Card(deck_id=deck.id, front=front, back=back)
    db.session.add(card)
    db.session.commit()

    if request.headers.get("HX-Request"):
        cards = Card.query.filter_by(deck_id=deck.id).order_by(Card.created_at.desc()).all()
        return render_template("decks/partials/card_list.html", deck=deck, cards=cards)

    flash("Card added.", "success")
    return redirect(url_for("decks.view_deck", deck_id=deck.id))


@decks_bp.route("/<int:deck_id>/cards/<int:card_id>/edit", methods=["GET", "POST"])
@login_required
def edit_card(deck_id, card_id):
    deck = get_deck_or_404(deck_id)
    card = db.session.get(Card, card_id)
    if not card or card.deck_id != deck.id:
        abort(404)

    if request.method == "POST":
        front = request.form.get("front", "").strip()
        back = request.form.get("back", "").strip()

        if not front or not back:
            flash("Both front and back are required.", "error")
            if request.headers.get("HX-Request"):
                return render_template("decks/partials/card_form.html", deck=deck, card=card)
            return redirect(url_for("decks.edit_card", deck_id=deck.id, card_id=card.id))

        card.front = front
        card.back = back
        db.session.commit()

        if request.headers.get("HX-Request"):
            return render_template("decks/partials/card_row.html", deck=deck, card=card)

        flash("Card updated.", "success")
        return redirect(url_for("decks.view_deck", deck_id=deck.id))

    if request.headers.get("HX-Request"):
        return render_template("decks/partials/card_form.html", deck=deck, card=card)

    return render_template("decks/edit_card.html", deck=deck, card=card)


@decks_bp.route("/<int:deck_id>/cards/<int:card_id>/delete", methods=["POST"])
@login_required
def delete_card(deck_id, card_id):
    deck = get_deck_or_404(deck_id)
    card = db.session.get(Card, card_id)
    if not card or card.deck_id != deck.id:
        abort(404)

    db.session.delete(card)
    db.session.commit()

    if request.headers.get("HX-Request"):
        return ""  # Remove the row

    flash("Card deleted.", "success")
    return redirect(url_for("decks.view_deck", deck_id=deck.id))


@decks_bp.route("/<int:deck_id>/import", methods=["GET", "POST"])
@login_required
def import_cards(deck_id):
    deck = get_deck_or_404(deck_id)

    if request.method == "POST":
        json_text = None

        # Check file upload first
        file = request.files.get("file")
        if file and file.filename:
            try:
                json_text = file.read().decode("utf-8")
            except UnicodeDecodeError:
                flash("File must be valid UTF-8 text.", "error")
                return render_template("decks/import.html", deck=deck), 400
        else:
            json_text = request.form.get("json_text", "").strip()

        if not json_text:
            flash("Please provide JSON data.", "error")
            return render_template("decks/import.html", deck=deck), 400

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            flash(f"Invalid JSON: {e}", "error")
            return render_template("decks/import.html", deck=deck), 400

        cards_data = data.get("cards", [])
        if not isinstance(cards_data, list):
            flash("JSON must contain a 'cards' array.", "error")
            return render_template("decks/import.html", deck=deck), 400

        if len(cards_data) > 1000:
            flash("Maximum 1000 cards per import.", "error")
            return render_template("decks/import.html", deck=deck), 400

        imported = 0
        errors = []
        for i, item in enumerate(cards_data):
            if not isinstance(item, dict):
                errors.append(f"Card {i+1}: not an object")
                continue
            front = item.get("front", "")
            back = item.get("back", "")
            if not isinstance(front, str) or not front.strip():
                errors.append(f"Card {i+1}: missing or invalid 'front'")
                continue
            if not isinstance(back, str) or not back.strip():
                errors.append(f"Card {i+1}: missing or invalid 'back'")
                continue

            card = Card(deck_id=deck.id, front=front.strip(), back=back.strip())
            db.session.add(card)
            imported += 1

        db.session.commit()

        if imported:
            flash(f"Successfully imported {imported} card(s).", "success")
        if errors:
            flash(f"Skipped {len(errors)} card(s): {'; '.join(errors[:5])}", "error")

        return redirect(url_for("decks.view_deck", deck_id=deck.id))

    return render_template("decks/import.html", deck=deck)
