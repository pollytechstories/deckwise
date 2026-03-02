import markdown
from markupsafe import Markup


_md = markdown.Markdown(
    extensions=["fenced_code", "codehilite", "tables", "nl2br"],
    extension_configs={
        "codehilite": {"css_class": "codehilite", "guess_lang": False},
    },
)


def render_markdown(text):
    """Convert markdown text to safe HTML."""
    if not text:
        return ""
    _md.reset()
    return Markup(_md.convert(text))
