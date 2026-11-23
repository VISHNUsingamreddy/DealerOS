import re
from decimal import Decimal, InvalidOperation


def normalize_ref(raw):
    """Normalize a B record reference by extracting its digits."""
    m = re.search(r"\d+", str(raw or "").strip())
    return f"REC-{m.group()}" if m else None


def parse_amount(raw):
    """Parse a money value; blank or non-finite/junk values are unknown."""
    s = str(raw or "").strip().replace(",", "")
    if not s:
        return None
    try:
        value = Decimal(s)
    except (InvalidOperation, ValueError):
        return None
    return value if value.is_finite() else None


def parse_date(raw):
    from datetime import date

    s = str(raw or "").strip()
    if not s:
        return None
    try:
        y, m, d = map(int, s.split("-"))
        return date(y, m, d)
    except (TypeError, ValueError):
        return None
