# DeckWise — Project Conventions

## Tech Stack
- Python 3.14 + Flask 3.1 (server-rendered)
- Jinja2 + HTMX 2.0 (dynamic interactions, no custom JS framework)
- SQLite + SQLAlchemy 2.0 (single-file DB, ORM)
- Pico CSS v2 (CDN, responsive, mobile-first)
- Markdown + Pygments (server-side rendering with syntax highlighting)
- Flask-Login + Flask-Bcrypt (session auth, bcrypt hashing)

## Project Structure
```
app.py                  # Entry point
config.py               # Config class
deckwise/
  __init__.py           # create_app() factory
  extensions.py         # db, login_manager, bcrypt, csrf
  models.py             # User, Deck, Card, ReviewLog
  sm2.py                # SM-2 spaced repetition algorithm
  markdown_utils.py     # render_markdown() Jinja2 filter
  auth/routes.py        # register, login, logout
  decks/routes.py       # deck CRUD, card CRUD, bulk import
  study/routes.py       # study session, reveal, rate
  templates/            # Jinja2 templates
  static/               # CSS + JS
```

## How to Run
```bash
source venv/bin/activate
pip install -r requirements.txt
python app.py
# → http://127.0.0.1:5000
```

## Python Environment
Use the `venv` virtualenv at project root (no dot prefix):
```bash
venv/bin/pip install -r requirements.txt
venv/bin/python app.py
```

## Key Patterns
- All datetimes are naive UTC (SQLite compatible)
- Deck ownership enforced on every route (returns 404, not 403)
- CSRF protection on all POST routes; HTMX sends token via `X-CSRFToken` header
- SM-2 quality mapping: Again=1, Hard=2, Good=3, Easy=5
- Markdown rendered server-side via Jinja2 filter `{{ text | markdown }}`
- HTMX partials in `templates/*/partials/` for dynamic swaps

## Database
SQLite at `instance/deckwise.db` (auto-created on first run).
Delete it to reset: `rm instance/deckwise.db`
