"""
estateflow/api/leads.py

Lead intake webhook + dashboard stats API.
"""

import frappe
from frappe.utils import today, now_datetime, add_days


# ── Lead Intake Webhook ───────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def intake_webhook():
    """
    POST /api/method/estateflow.api.leads.intake_webhook

    Accepts leads from 36 Acre, MagicBricks, Facebook Lead Ads,
    Zapier, Make, website forms, etc.

    Headers:
        Content-Type: application/json
        X-Webhook-Secret: <your secret from EF Integration Settings>

    Body:
    {
        "fullName": "Rahul Sharma",
        "phone": "+919999999999",
        "email": "rahul@example.com",
        "source": "36 Acre",
        "propertyType": "Apartment",
        "budgetMin": 7500000,
        "budgetMax": 12000000,
        "preferredLocation": "Gurgaon",
        "notes": "Looking for 3BHK near Golf Course Road"
    }
    """
    # Validate secret
    settings = frappe.get_single("EF Integration Settings")
    secret = settings.get_password("webhook_secret") if settings.get("webhook_secret") else None
    if secret:
        incoming = frappe.request.headers.get("X-Webhook-Secret", "")
        if incoming != secret:
            frappe.throw("Unauthorized", frappe.AuthenticationError)

    data = frappe.request.get_json(force=True) or {}

    # Required fields
    full_name = data.get("fullName", "").strip()
    phone = data.get("phone", "").strip()
    if not full_name:
        frappe.throw("fullName is required")
    if not phone:
        frappe.throw("phone is required")

    # Source mapping
    source_map = {
        "36acre": "36 Acre", "36 acre": "36 Acre",
        "magicbricks": "MagicBricks",
        "housing.com": "Housing.com", "housing": "Housing.com",
        "facebook": "Facebook", "fb": "Facebook",
        "instagram": "Instagram",
        "website": "Website",
        "referral": "Referral",
        "manual": "Manual",
    }
    raw_source = str(data.get("source", "Other")).strip()
    source = source_map.get(raw_source.lower(), raw_source)

    # Round-robin agent assignment
    from estateflow.api.calls import _get_next_agent
    agent_email = _get_next_agent()

    # Split name
    parts = full_name.split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    # Create CRM Lead (triggers on_new_lead → bridge call)
    lead = frappe.new_doc("CRM Lead")
    lead.first_name = first_name
    lead.last_name = last_name
    lead.lead_name = full_name
    lead.mobile_no = phone
    lead.email_id = data.get("email", "")
    lead.source = source
    lead.lead_owner = agent_email or ""
    lead.notes = data.get("notes", "")
    lead.status = "New"

    # Custom EstateFlow fields
    lead.ef_property_type = data.get("propertyType", "")
    lead.ef_budget_min = data.get("budgetMin") or 0
    lead.ef_budget_max = data.get("budgetMax") or 0
    lead.ef_preferred_location = data.get("preferredLocation", "")
    lead.ef_lead_temperature = "Warm"
    lead.ef_call_status = "Call Pending"

    lead.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "lead": lead.name,
        "lead_name": full_name,
        "assigned_agent": agent_email,
        "message": f"Lead '{full_name}' created and assigned to {agent_email or 'unassigned'}",
    }


# ── Dashboard API ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_dashboard_stats():
    """Return key metrics for the EstateFlow dashboard."""
    today_str = today()

    new_today = frappe.db.count("CRM Lead", {"DATE(creation)": today_str})
    hot_leads = frappe.db.count("CRM Lead", {"ef_lead_temperature": "Hot"})

    followups_due = frappe.db.count(
        "EF Follow Up",
        {"status": "Pending", "scheduled_at": ("<=", now_datetime())},
    )

    calls_today = frappe.db.count("EF Call Log", {"DATE(started_at)": today_str})

    available_props = frappe.db.count("EF Property", {"availability_status": "Available"})

    # Leads by status
    by_status = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabCRM Lead`
        GROUP BY status
        ORDER BY count DESC
    """, as_dict=True)

    # Leads by source (last 30 days)
    by_source = frappe.db.sql("""
        SELECT source, COUNT(*) as count
        FROM `tabCRM Lead`
        WHERE creation >= %s
        GROUP BY source
        ORDER BY count DESC
        LIMIT 8
    """, (add_days(today_str, -30),), as_dict=True)

    # Checked in today
    checked_in = frappe.db.count(
        "EF Attendance Log",
        {"attendance_date": today_str, "check_in_time": ("is", "set")},
    )

    return {
        "new_leads_today": new_today,
        "hot_leads": hot_leads,
        "followups_due": followups_due,
        "calls_today": calls_today,
        "available_properties": available_props,
        "checked_in_today": checked_in,
        "leads_by_status": by_status,
        "leads_by_source": by_source,
    }


@frappe.whitelist()
def get_hot_leads(limit=5):
    return frappe.get_list(
        "CRM Lead",
        filters={"ef_lead_temperature": "Hot"},
        fields=[
            "name", "lead_name", "mobile_no", "email_id", "source",
            "status", "ef_lead_temperature", "ef_property_type",
            "ef_budget_min", "ef_budget_max", "ef_preferred_location",
            "ef_next_followup", "ef_last_contacted", "creation", "modified",
        ],
        order_by="modified desc",
        limit=int(limit),
    )


@frappe.whitelist()
def get_leads(status=None, source=None, temperature=None, ef_property_type=None, search=None, limit=50, start=0):
    filters = {}
    if status:
        filters["status"] = status
    if source:
        filters["source"] = source
    if temperature:
        filters["ef_lead_temperature"] = temperature
    if ef_property_type:
        filters["ef_property_type"] = ef_property_type

    leads = frappe.get_list(
        "CRM Lead",
        filters=filters,
        fields=[
            "name", "lead_name", "mobile_no", "email_id", "source",
            "status", "ef_lead_temperature", "ef_property_type",
            "ef_budget_min", "ef_budget_max", "ef_preferred_location",
            "ef_next_followup", "ef_last_contacted", "ef_call_status",
            "lead_owner", "creation", "modified",
        ],
        order_by="modified desc",
        limit=int(limit),
        start=int(start),
    )

    if search:
        search_lower = search.lower()
        leads = [
            l for l in leads
            if search_lower in (l.lead_name or "").lower()
            or search_lower in (l.mobile_no or "").lower()
            or search_lower in (l.email_id or "").lower()
            or search_lower in (l.ef_preferred_location or "").lower()
        ]

    return leads


@frappe.whitelist()
def get_lead(lead_name):
    lead = frappe.get_doc("CRM Lead", lead_name)
    return lead.as_dict()


@frappe.whitelist()
def update_lead(lead_name, data):
    if isinstance(data, str):
        import json
        data = json.loads(data)
    lead = frappe.get_doc("CRM Lead", lead_name)
    lead.update(data)
    lead.save(ignore_permissions=True)
    frappe.db.commit()
    return lead.as_dict()


@frappe.whitelist()
def get_agents():
    """Return all sales users for agent assignment."""
    agents = frappe.get_list(
        "Has Role",
        filters={"role": "Sales User", "parenttype": "User"},
        fields=["parent as email"],
        as_list=False,
    )
    result = []
    for a in agents:
        user = frappe.db.get_value(
            "User", a["email"],
            ["full_name", "mobile_no", "user_image"],
            as_dict=True,
        )
        if user:
            result.append({"email": a["email"], **user})
    return result


@frappe.whitelist()
def get_lead_count():
    """Quick count for dashboard badges."""
    return {
        "total": frappe.db.count("CRM Lead"),
        "hot": frappe.db.count("CRM Lead", {"ef_lead_temperature": "Hot"}),
        "new_today": frappe.db.count("CRM Lead", {"DATE(creation)": frappe.utils.today()}),
    }
