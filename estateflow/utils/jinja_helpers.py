"""
estateflow/utils/jinja_helpers.py
Global helper functions registered in hooks.py → jinja.methods
Available as {{ format_inr(price) }} etc. in all Jinja templates.
"""


def format_inr(amount):
    """Format a number as Indian currency string: ₹45L, ₹2.5 Cr, etc."""
    if not amount:
        return "—"
    n = float(amount)
    if n >= 10_000_000:
        return f"₹{n / 10_000_000:.2f} Cr"
    if n >= 100_000:
        return f"₹{n / 100_000:.0f}L"
    return f"₹{n:,.0f}"


_AVATAR_COLORS = [
    ("#ede9fe", "#6d28d9"),
    ("#dbeafe", "#1d4ed8"),
    ("#dcfce7", "#15803d"),
    ("#ffedd5", "#c2410c"),
    ("#fce7f3", "#be185d"),
    ("#e0f2fe", "#0369a1"),
]


def lead_avatar_color(name):
    """Return (bg, fg) hex pair for a lead's avatar based on their name."""
    idx = (ord((name or "A")[0])) % len(_AVATAR_COLORS)
    return _AVATAR_COLORS[idx]


def lead_initials(name):
    """Return up to 2 initials from a full name string."""
    if not name:
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return parts[0][0].upper()
