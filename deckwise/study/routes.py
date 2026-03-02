from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models import Deck, Card, ReviewLog
from ..sm2 import sm2

study_bp = Blueprint("study", __name__, url_prefix="/study")


def get_deck_or_404(deck_id):
    deck = db.session.get(Deck, deck_id)
    if not deck or deck.user_id != current_user.id:
        abort(404)
    return deck


def get_next_due_card(deck_id):
    now = datetime.utcnow()
    return (
        Card.query
        .filter(Card.deck_id == deck_id, Card.next_review <= now)
        .order_by(Card.next_review)
        .first()
    )


def count_due_cards(deck_id):
    now = datetime.utcnow()
    return Card.query.filter(Card.deck_id == deck_id, Card.next_review <= now).count()


@study_bp.route("/<int:deck_id>")
@login_required
def session(deck_id):
    deck = get_deck_or_404(deck_id)
    due = count_due_cards(deck.id)
    return render_template("study/session.html", deck=deck, due_count=due)


@study_bp.route("/<int:deck_id>/card")
@login_required
def next_card(deck_id):
    deck = get_deck_or_404(deck_id)
    card = get_next_due_card(deck.id)
    remaining = count_due_cards(deck.id)

    if not card:
        return render_template("study/partials/session_complete.html", deck=deck)

    return render_template("study/partials/card_front.html", deck=deck, card=card, remaining=remaining)


@study_bp.route("/<int:deck_id>/card/<int:card_id>/reveal", methods=["POST"])
@login_required
def reveal(deck_id, card_id):
    deck = get_deck_or_404(deck_id)
    card = db.session.get(Card, card_id)
    if not card or card.deck_id != deck.id:
        abort(404)

    remaining = count_due_cards(deck.id)
    return render_template("study/partials/card_back.html", deck=deck, card=card, remaining=remaining)


@study_bp.route("/<int:deck_id>/card/<int:card_id>/rate", methods=["POST"])
@login_required
def rate(deck_id, card_id):
    deck = get_deck_or_404(deck_id)
    card = db.session.get(Card, card_id)
    if not card or card.deck_id != deck.id:
        abort(404)

    quality = request.form.get("quality", type=int)
    if quality is None or quality < 0 or quality > 5:
        abort(400)

    # Save pre-review state
    ef_before = card.ease_factor
    interval_before = card.interval

    # Run SM-2
    new_reps, new_ef, new_interval, next_review = sm2(
        quality=quality,
        repetitions=card.repetitions,
        ease_factor=card.ease_factor,
        interval=card.interval,
    )

    # Update card
    card.repetitions = new_reps
    card.ease_factor = new_ef
    card.interval = new_interval
    card.next_review = next_review

    # Log review
    log = ReviewLog(
        card_id=card.id,
        quality=quality,
        ease_factor_before=ef_before,
        ease_factor_after=new_ef,
        interval_before=interval_before,
        interval_after=new_interval,
    )
    db.session.add(log)
    db.session.commit()

    # Return next card
    next_card = get_next_due_card(deck.id)
    remaining = count_due_cards(deck.id)

    if not next_card:
        return render_template("study/partials/session_complete.html", deck=deck)

    return render_template("study/partials/card_front.html", deck=deck, card=next_card, remaining=remaining)
