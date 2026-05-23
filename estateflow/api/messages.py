"""
estateflow/api/messages.py

WhatsApp & SMS service via Twilio.
DRY-RUN by default — configure EF Integration Settings to send real messages.
"""

import frappe
from frappe.utils import now_datetime


# ── Built-in templates (also seeded via fixtures) ─────────────────────────────

DEFAULT_TEMPLATES = [
    {
        "name": "Quick Check-in",
        "channel": "WhatsApp",
        "body": "Hi {{lead_name}}, just checking if you had a chance to review the property details I shared. Let me know if you have any questions! 🏠",
    },
    {
        "name": "Invite for Call",
        "channel": "WhatsApp",
        "body": "Hi {{lead_name}}, are you available for a quick call today to discuss properties in {{preferred_location}}? I have some great options for you. 📞",
    },
    {
        "name": "New Options Available",
        "channel": "WhatsApp",
        "body": "Hi {{lead_name}}, we have a few new options matching your budget. Should I share them? 🏡",
    },
    {
        "name": "Site Visit Invite",
        "channel": "WhatsApp",
        "body": "Hi {{lead_name}}, would you like to schedule a site visit this week? Seeing the property in person helps make the best decision. 🗓️",
    },
    {
        "name": "Re-engage",
        "channel": "WhatsApp",
        "body": "Hi {{lead_name}}, hope you are doing well! We have new listings that might interest you. Would you like to take a look? 😊",
    },
]


# ── Whitelisted API ───────────────────────────────────────────────────────────

@frappe.whitelist()
def get_templates():
    """Return all message templates."""
    db_templates = frappe.get_list(
        "EF Message Template",
        fields=["name", "template_name", "channel", "body"],
        order_by="template_name asc",
    )
    return db_templates or DEFAULT_TEMPLATES


@frappe.whitelist()
def send_follow_up(lead_name, template_name, channel="WhatsApp"):
    """
    POST /api/method/estateflow.api.messages.send_follow_up
    Send a follow-up message to a lead via WhatsApp/SMS.
    """
    lead = frappe.get_doc("CRM Lead", lead_name)
    settings = frappe.get_single("EF Integration Settings")
    agent_email = frappe.session.user

    # Resolve template body
    message = _render_template(template_name, lead)

    dry_run = bool(
        settings.get("whatsapp_dry_run")
        or not settings.get("whatsapp_sender")
        or not settings.get("twilio_account_sid")
    )

    if dry_run:
        log = _create_follow_up_log(lead.name, agent_email, channel, message, "Dry Run")
        frappe.db.commit()
        return {
            "success": True,
            "dry_run": True,
            "follow_up": log.name,
            "preview": message,
            "message": f"[DRY-RUN] {channel} would be sent to {lead.mobile_no or lead.phone}. Configure WhatsApp in EF Integration Settings.",
        }

    result = _send_twilio_message(
        to=lead.mobile_no or lead.phone,
        body=message,
        channel=channel,
        settings=settings,
    )

    status = "Sent" if result["success"] else "Failed"
    log = _create_follow_up_log(lead.name, agent_email, channel, message, status)

    if result["success"]:
        frappe.db.set_value("CRM Lead", lead.name, "ef_last_contacted", now_datetime())

    frappe.db.commit()
    return {**result, "follow_up": log.name, "preview": message}


@frappe.whitelist()
def send_property_share(lead_name, property_name, channel="WhatsApp"):
    """
    POST /api/method/estateflow.api.messages.send_property_share
    Share a property with a lead via WhatsApp/SMS.
    """
    lead = frappe.get_doc("CRM Lead", lead_name)
    prop = frappe.get_doc("EF Property", property_name)
    settings = frappe.get_single("EF Integration Settings")
    agent_email = frappe.session.user

    message = prop.get_whatsapp_message(lead.lead_name)
    share_link = prop.get_share_url()

    dry_run = bool(
        settings.get("whatsapp_dry_run")
        or not settings.get("whatsapp_sender")
        or not settings.get("twilio_account_sid")
    )

    if dry_run:
        log = _create_follow_up_log(lead.name, agent_email, channel, message, "Dry Run")
        frappe.db.commit()
        return {
            "success": True,
            "dry_run": True,
            "follow_up": log.name,
            "share_link": share_link,
            "preview": message,
            "message": f"[DRY-RUN] Property details would be sent via {channel}.",
        }

    result = _send_twilio_message(
        to=lead.mobile_no or lead.phone,
        body=message,
        channel=channel,
        settings=settings,
    )

    status = "Sent" if result["success"] else "Failed"
    log = _create_follow_up_log(lead.name, agent_email, channel, message, status)
    frappe.db.commit()
    return {**result, "follow_up": log.name, "share_link": share_link, "preview": message}


@frappe.whitelist()
def get_lead_follow_ups(lead_name):
    """Return follow-up history for a lead."""
    return frappe.get_list(
        "EF Follow Up",
        filters={"lead": lead_name},
        fields=["name", "channel", "status", "message", "sent_at", "dry_run", "agent"],
        order_by="sent_at desc",
        limit=20,
    )


@frappe.whitelist()
def get_lead_calls(lead_name):
    """Return call history for a lead."""
    return frappe.get_list(
        "EF Call Log",
        filters={"lead": lead_name},
        fields=["name", "call_status", "started_at", "ended_at", "duration_seconds", "outcome", "dry_run", "agent"],
        order_by="started_at desc",
        limit=20,
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _render_template(template_name, lead):
    """Fetch template from DB or defaults, fill variables."""
    body = None
    try:
        tmpl = frappe.get_doc("EF Message Template", template_name)
        body = tmpl.body
    except Exception:
        for t in DEFAULT_TEMPLATES:
            if t["name"] == template_name:
                body = t["body"]
                break

    if not body:
        body = f"Hi {{{{lead_name}}}}, following up on your property inquiry."

    vars = {
        "lead_name": lead.lead_name or lead.first_name or "there",
        "preferred_location": lead.get("ef_preferred_location") or "your preferred area",
        "phone": lead.mobile_no or lead.phone or "",
    }
    for key, val in vars.items():
        body = body.replace("{{" + key + "}}", str(val))
    return body


def _send_twilio_message(to, body, channel, settings):
    try:
        from twilio.rest import Client
        client = Client(
            settings.twilio_account_sid,
            settings.get_password("twilio_auth_token"),
        )
        sender = settings.whatsapp_sender
        if channel == "WhatsApp":
            from_number = f"whatsapp:{sender}"
            to_number = f"whatsapp:{to}"
        else:
            from_number = sender
            to_number = to

        msg = client.messages.create(to=to_number, from_=from_number, body=body)
        return {"success": True, "dry_run": False, "message_sid": msg.sid}
    except ImportError:
        return {"success": False, "error": "Twilio library not installed. Run: pip install twilio"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "EstateFlow: Twilio message error")
        return {"success": False, "error": str(e)}


def _create_follow_up_log(lead_name, agent_email, channel, message, status):
    doc = frappe.new_doc("EF Follow Up")
    doc.lead = lead_name
    doc.agent = agent_email
    doc.channel = channel
    doc.message = message
    doc.status = status
    doc.dry_run = 1 if status == "Dry Run" else 0
    doc.sent_at = now_datetime() if status in ("Sent", "Dry Run") else None
    doc.insert(ignore_permissions=True)
    return doc
