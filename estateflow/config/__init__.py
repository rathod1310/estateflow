import frappe


def get_settings():
    """Return cached integration settings doc."""
    try:
        return frappe.get_single("EF Integration Settings")
    except Exception:
        return frappe._dict()


def is_twilio_configured():
    s = get_settings()
    return bool(
        getattr(s, "twilio_account_sid", None)
        and getattr(s, "twilio_auth_token", None)
        and getattr(s, "twilio_phone_number", None)
    )


def is_whatsapp_configured():
    s = get_settings()
    return bool(getattr(s, "whatsapp_sender", None)) and is_twilio_configured()


def get_twilio_client():
    """Return a Twilio REST client or None in dry-run mode."""
    if not is_twilio_configured():
        return None
    try:
        from twilio.rest import Client
        s = get_settings()
        return Client(s.twilio_account_sid, s.get_password("twilio_auth_token"))
    except ImportError:
        frappe.log_error("Twilio library not installed. Run: pip install twilio")
        return None
