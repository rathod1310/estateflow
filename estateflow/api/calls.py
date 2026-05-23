"""
estateflow/api/calls.py

Twilio Voice bridge service.

DRY-RUN MODE (default): when EF Integration Settings has twilio_dry_run=1
or Twilio credentials are missing, all calls are simulated and logged.

Production flow:
  1. New CRM Lead created → on_new_lead() triggered via doc_events
  2. System calls assigned agent first
  3. Agent hears: "New lead from {source}. Press any key to connect."
  4. Agent presses key → lead is called → both bridged in TwiML Conference
  5. EF Call Log created with result
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, get_url


# ── Frappe doc_event hook ─────────────────────────────────────────────────────

def on_new_lead(doc, method=None):
    """Called automatically after a new CRM Lead is inserted."""
    try:
        agent_email = doc.lead_owner or _get_next_agent()
        if not agent_email:
            frappe.log_error("No agent available for lead bridge call", "EstateFlow Calls")
            return
        initiate_bridge_call(lead_name=doc.name, agent_email=agent_email)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "EstateFlow: on_new_lead call error")


# ── Whitelisted API endpoints ─────────────────────────────────────────────────

@frappe.whitelist()
def initiate_bridge_call(lead_name, agent_email=None):
    """
    POST /api/method/estateflow.api.calls.initiate_bridge_call
    Initiates the agent-first → lead bridge call for a given lead.
    """
    lead = frappe.get_doc("CRM Lead", lead_name)
    if not agent_email:
        agent_email = lead.lead_owner or _get_next_agent()

    settings = frappe.get_single("EF Integration Settings")
    dry_run = _is_dry_run(settings)

    if dry_run:
        log = _create_call_log(lead.name, agent_email, dry_run=True)
        frappe.db.commit()
        return {
            "success": True,
            "dry_run": True,
            "call_log": log.name,
            "message": f"[DRY-RUN] Would call agent {agent_email} then bridge to {lead.lead_name} ({lead.mobile_no or lead.phone}). Configure Twilio in EF Integration Settings for real calls.",
        }

    client = _get_twilio_client(settings)
    if not client:
        return {"success": False, "error": "Twilio not configured"}

    conference_name = f"ef-bridge-{lead.name}-{frappe.generate_hash(length=8)}"
    app_url = get_url()

    # Call the agent first
    agent_user = frappe.get_doc("User", agent_email)
    agent_phone = agent_user.mobile_no or agent_user.phone
    if not agent_phone:
        return {"success": False, "error": f"Agent {agent_email} has no phone number configured"}

    try:
        call = client.calls.create(
            to=agent_phone,
            from_=settings.twilio_phone_number,
            url=f"{app_url}/api/method/estateflow.api.calls.twiml_agent"
                f"?lead_name={frappe.utils.quote(lead.name)}"
                f"&conference_name={conference_name}"
                f"&lead_phone={frappe.utils.quote(lead.mobile_no or lead.phone or '')}"
                f"&lead_display={frappe.utils.quote(lead.lead_name or '')}"
                f"&source={frappe.utils.quote(lead.source or 'Platform')}",
            status_callback=f"{app_url}/api/method/estateflow.api.calls.twilio_status_callback",
            status_callback_method="POST",
        )
        log = _create_call_log(lead.name, agent_email, call_sid=call.sid, dry_run=False)
        frappe.db.set_value("CRM Lead", lead.name, "ef_call_status", "Called")
        frappe.db.commit()
        return {
            "success": True,
            "dry_run": False,
            "call_log": log.name,
            "call_sid": call.sid,
            "message": f"Calling agent {agent_email} first. Will bridge to lead on answer.",
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "EstateFlow: Twilio call error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def direct_call_lead(lead_name):
    """
    One-click direct call to lead (no agent bridge, simpler flow).
    POST /api/method/estateflow.api.calls.direct_call_lead
    """
    lead = frappe.get_doc("CRM Lead", lead_name)
    settings = frappe.get_single("EF Integration Settings")
    agent_email = frappe.session.user
    dry_run = _is_dry_run(settings)

    if dry_run:
        log = _create_call_log(lead.name, agent_email, dry_run=True)
        frappe.db.commit()
        return {
            "success": True,
            "dry_run": True,
            "call_log": log.name,
            "message": f"[DRY-RUN] Would call {lead.lead_name} at {lead.mobile_no or lead.phone}",
        }

    client = _get_twilio_client(settings)
    if not client:
        return {"success": False, "error": "Twilio not configured"}

    app_url = get_url()
    try:
        call = client.calls.create(
            to=lead.mobile_no or lead.phone,
            from_=settings.twilio_phone_number,
            url=f"{app_url}/api/method/estateflow.api.calls.twiml_direct",
        )
        log = _create_call_log(lead.name, agent_email, call_sid=call.sid, dry_run=False)
        frappe.db.set_value("CRM Lead", lead.name, {
            "ef_call_status": "Called",
            "ef_last_contacted": now_datetime(),
        })
        frappe.db.commit()
        return {"success": True, "dry_run": False, "call_log": log.name, "call_sid": call.sid}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "EstateFlow: direct call error")
        return {"success": False, "error": str(e)}


# ── TwiML endpoints (called by Twilio, must be guest-accessible) ──────────────

@frappe.whitelist(allow_guest=True)
def twiml_agent(**kwargs):
    """
    Twilio calls this URL when the agent answers.
    Returns TwiML: play message → gather keypress → connect to conference.
    """
    lead_display = kwargs.get("lead_display", "the lead")
    source = kwargs.get("source", "our platform")
    conference_name = kwargs.get("conference_name", "")
    lead_phone = kwargs.get("lead_phone", "")
    lead_name = kwargs.get("lead_name", "")
    app_url = get_url()

    frappe.local.response.update({
        "type": "text",
        "http_status_code": 200,
    })
    frappe.local.response["content_type"] = "text/xml"
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather numDigits="1" action="{app_url}/api/method/estateflow.api.calls.twiml_agent_confirm?conference_name={conference_name}&amp;lead_phone={frappe.utils.quote(lead_phone)}&amp;lead_name={frappe.utils.quote(lead_name)}" method="POST">
    <Say voice="Polly.Aditi" language="en-IN">
      New real estate lead from {source}. Lead name is {lead_display}.
      Press any key to connect with the lead now.
    </Say>
    <Pause length="2"/>
    <Say voice="Polly.Aditi" language="en-IN">Press any key to connect.</Say>
  </Gather>
  <Say voice="Polly.Aditi" language="en-IN">No response received. Goodbye.</Say>
</Response>"""
    return twiml


@frappe.whitelist(allow_guest=True)
def twiml_agent_confirm(**kwargs):
    """Agent pressed a key. Add to conference and call the lead."""
    conference_name = kwargs.get("conference_name", "")
    lead_phone = kwargs.get("lead_phone", "")
    lead_name_doc = kwargs.get("lead_name", "")
    app_url = get_url()

    # Place outbound call to lead
    if lead_phone:
        try:
            settings = frappe.get_single("EF Integration Settings")
            client = _get_twilio_client(settings)
            if client:
                client.calls.create(
                    to=lead_phone,
                    from_=settings.twilio_phone_number,
                    url=f"{app_url}/api/method/estateflow.api.calls.twiml_lead?conference_name={conference_name}",
                )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "EstateFlow: lead call in confirm")

    frappe.local.response["content_type"] = "text/xml"
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">Connecting you to the lead now. Please hold.</Say>
  <Dial>
    <Conference
      waitUrl="http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical"
      startConferenceOnEnter="true"
      endConferenceOnExit="true"
      record="record-from-start"
    >{conference_name}</Conference>
  </Dial>
</Response>"""
    return twiml


@frappe.whitelist(allow_guest=True)
def twiml_lead(**kwargs):
    """TwiML played to the lead when they pick up."""
    conference_name = kwargs.get("conference_name", "")
    frappe.local.response["content_type"] = "text/xml"
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    Hello! Please hold while we connect you to our property consultant.
  </Say>
  <Dial>
    <Conference
      waitUrl="http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical"
      startConferenceOnEnter="true"
      endConferenceOnExit="false"
    >{conference_name}</Conference>
  </Dial>
</Response>"""
    return twiml


@frappe.whitelist(allow_guest=True)
def twiml_direct(**kwargs):
    """Simple direct call TwiML."""
    frappe.local.response["content_type"] = "text/xml"
    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    Hello! Your property consultant is calling. Please stay on the line.
  </Say>
</Response>"""


@frappe.whitelist(allow_guest=True)
def twilio_status_callback(**kwargs):
    """Twilio posts call status updates here."""
    call_sid = kwargs.get("CallSid", "")
    call_status = kwargs.get("CallStatus", "")
    duration = kwargs.get("CallDuration", 0)
    recording_url = kwargs.get("RecordingUrl", "")

    if call_sid:
        logs = frappe.get_list("EF Call Log", filters={"call_sid": call_sid}, limit=1)
        if logs:
            status_map = {
                "completed": "Completed", "no-answer": "No Answer",
                "busy": "Busy", "failed": "Failed", "in-progress": "In Progress",
            }
            frappe.db.set_value("EF Call Log", logs[0].name, {
                "call_status": status_map.get(call_status, call_status.title()),
                "duration_seconds": int(duration) if duration else 0,
                "recording_url": recording_url,
                "ended_at": now_datetime(),
            })
            frappe.db.commit()
    return "ok"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _is_dry_run(settings=None):
    if settings is None:
        settings = frappe.get_single("EF Integration Settings")
    return bool(
        settings.get("twilio_dry_run")
        or not settings.get("twilio_account_sid")
        or not settings.get("twilio_phone_number")
    )


def _get_twilio_client(settings=None):
    from estateflow.config import get_twilio_client
    return get_twilio_client()


def _create_call_log(lead_name, agent_email, call_sid=None, dry_run=False):
    from estateflow.doctype.ef_call_log.ef_call_log import EFCallLog
    return EFCallLog.create_for_lead(lead_name, agent_email, call_sid=call_sid, dry_run=dry_run)


def _get_next_agent():
    """Round-robin: pick the sales user with fewest calls today."""
    from frappe.utils import today
    sales_users = frappe.get_list(
        "Has Role",
        filters={"role": "Sales User", "parenttype": "User"},
        fields=["parent"],
        as_list=True,
    )
    if not sales_users:
        return None

    user_emails = [u[0] for u in sales_users]
    # Count calls today per user
    call_counts = {e: 0 for e in user_emails}
    today_calls = frappe.db.sql("""
        SELECT agent, COUNT(*) as cnt
        FROM `tabEF Call Log`
        WHERE DATE(started_at) = %s AND agent IN %s
        GROUP BY agent
    """, (today(), tuple(user_emails) if len(user_emails) > 1 else (user_emails[0], user_emails[0])), as_dict=True)
    for row in today_calls:
        call_counts[row.agent] = row.cnt

    # Return user with lowest call count
    return min(call_counts, key=call_counts.get)
