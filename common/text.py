"""Small text helpers shared by the checks."""
import re
import unicodedata

_QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "}


def norm(s: str) -> str:
    """Lowercase, straighten quotes and dashes, drop markdown emphasis, squash whitespace."""
    s = unicodedata.normalize("NFKC", s or "")
    for a, b in _QUOTES.items():
        s = s.replace(a, b)
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def quote_in(quote: str, source: str) -> bool:
    """True if the quote appears in the source, ignoring case, spacing and punctuation at the ends."""
    q = norm(quote).strip(" .,;:-\"'")
    return bool(q) and q in norm(source)
