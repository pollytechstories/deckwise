# DeckWise

A spaced-repetition flashcard web app with Markdown support, bulk import, and the SM-2 scheduling algorithm.

## Features

- **Spaced Repetition (SM-2)** — scientifically-backed review scheduling that adapts to your performance
- **Markdown & Code Highlighting** — write flashcards with full Markdown, including fenced code blocks with syntax highlighting
- **Bulk Import** — paste JSON or upload a file to import hundreds of cards at once (great for AI-generated content)
- **Multi-User** — each user has their own decks and cards with session-based auth
- **Mobile-Friendly** — responsive design that works on any device
- **HTMX-Powered** — smooth, dynamic interactions without page reloads

## Installation

```bash
# Clone and enter the project
cd deckwise

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Usage

1. **Register** an account and log in
2. **Create a deck** from the dashboard
3. **Add cards** manually or use bulk import
4. **Study** — cards due for review appear in study sessions
5. **Rate** your recall: Again, Hard, Good, or Easy

## Bulk Import

Generate flashcards with AI and import them as JSON:

```json
{
  "cards": [
    {
      "front": "What is a closure?",
      "back": "A function that captures variables from its enclosing scope.\n\n```python\ndef make_adder(n):\n    return lambda x: x + n\n```"
    },
    {
      "front": "What does `O(log n)` mean?",
      "back": "The algorithm's time grows **logarithmically** with input size.\n\nExample: binary search halves the search space each step."
    }
  ]
}
```

- Both `front` and `back` support Markdown with code blocks
- Maximum 1000 cards per import, 5MB file limit
- Invalid cards are skipped with an error summary

## How Spaced Repetition Works

DeckWise uses the **SM-2 algorithm**:

| Button | Effect |
|--------|--------|
| **Again** (red) | Reset — review again tomorrow |
| **Hard** (orange) | Reset — review again tomorrow, slight ease decrease |
| **Good** (blue) | Advance schedule (1d → 6d → interval × ease factor) |
| **Easy** (green) | Advance schedule with ease increase |

Cards you know well are shown less frequently. Cards you struggle with come back sooner. The ease factor adjusts automatically based on your performance history.
