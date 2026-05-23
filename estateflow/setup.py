"""
estateflow/setup.py
Runs automatically after: bench install-app estateflow
"""
import frappe


def after_install():
    """Post-install setup: create default settings, seed templates, add roles."""
    print("[EstateFlow] Running post-install setup...")

    _create_integration_settings()
    _seed_message_templates()
    _create_roles()
    _create_custom_fields()

    frappe.db.commit()
    print("[EstateFlow] ✅ Setup complete. Visit /estateflow to get started.")


# ── Integration Settings singleton ────────────────────────────────────────────

def _create_integration_settings():
    if frappe.db.exists("EF Integration Settings", "EF Integration Settings"):
        return
    doc = frappe.new_doc("EF Integration Settings")
    doc.twilio_dry_run = 1
    doc.whatsapp_dry_run = 1
    doc.lead_assignment_mode = "Round Robin"
    doc.insert(ignore_permissions=True)
    print("[EstateFlow]  → Integration Settings created (dry-run mode ON)")


# ── Default message templates ─────────────────────────────────────────────────

def _seed_message_templates():
    templates = [
        {
            "template_name": "Quick Check-in",
            "channel": "WhatsApp",
            "body": "Hi {{lead_name}}, just checking if you had a chance to review the property details I shared. Let me know if you have any questions! 🏠",
            "is_default": 1,
        },
        {
            "template_name": "Invite for Call",
            "channel": "WhatsApp",
            "body": "Hi {{lead_name}}, are you available for a quick call today to discuss properties in {{preferred_location}}? I have some great options for you. 📞",
        },
        {
            "template_name": "New Options Available",
            "channel": "WhatsApp",
            "body": "Hi {{lead_name}}, we have a few new options matching your budget. Should I share them? 🏡",
        },
        {
            "template_name": "Site Visit Invite",
            "channel": "WhatsApp",
            "body": "Hi {{lead_name}}, would you like to schedule a site visit this week? Seeing the property in person helps make the best decision. 🗓️",
        },
        {
            "template_name": "Re-engage",
            "channel": "WhatsApp",
            "body": "Hi {{lead_name}}, hope you are doing well! We have new listings that might interest you. Would you like to take a look? 😊",
        },
        {
            "template_name": "Property Share",
            "channel": "WhatsApp",
            "body": "Hi {{lead_name}}, sharing details of *{{property_title}}* in {{location}}.\n💰 Price: {{price}}\n📸 Photos & Details: {{share_link}}\n\nLet me know if you'd like to schedule a visit! 😊",
        },
        {
            "template_name": "SMS Follow-up",
            "channel": "SMS",
            "body": "Hi {{lead_name}}, following up on your property inquiry. Call us at any time. - EstateFlow Team",
        },
    ]

    for t in templates:
        if not frappe.db.exists("EF Message Template", t["template_name"]):
            doc = frappe.new_doc("EF Message Template")
            doc.update(t)
            doc.insert(ignore_permissions=True)

    print(f"[EstateFlow]  → {len(templates)} message templates seeded")


# ── Roles ─────────────────────────────────────────────────────────────────────

def _create_roles():
    roles = [
        {"role_name": "Sales User", "desk_access": 1},
        {"role_name": "Sales Manager", "desk_access": 1},
        {"role_name": "Field Executive", "desk_access": 0},
    ]
    for r in roles:
        if not frappe.db.exists("Role", r["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = r["role_name"]
            role.desk_access = r.get("desk_access", 0)
            role.insert(ignore_permissions=True)
    print("[EstateFlow]  → Roles ensured")


# ── Custom fields on CRM Lead ─────────────────────────────────────────────────

def _create_custom_fields():
    """
    Programmatically create custom fields on CRM Lead.
    Skipped gracefully if CRM Lead DocType is not installed (frappe-crm not present).
    """
    if not frappe.db.exists("DocType", "CRM Lead"):
        print("[EstateFlow]  ℹ CRM Lead DocType not found — skipping custom fields.")
        print("[EstateFlow]    Install frappe-crm app and run: bench --site <site> migrate")
        return
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    fields = {
        "CRM Lead": [
            {
                "fieldname": "ef_section_estateflow",
                "fieldtype": "Section Break",
                "label": "EstateFlow",
                "insert_after": "notes",
                "module": "EstateFlow CRM",
            },
            {
                "fieldname": "ef_property_type",
                "fieldtype": "Select",
                "label": "Interested Property Type",
                "options": "\nApartment\nVilla\nPlot\nCommercial\nRental",
                "insert_after": "ef_section_estateflow",
                "in_standard_filter": 1,
            },
            {
                "fieldname": "ef_budget_min",
                "fieldtype": "Currency",
                "label": "Budget Min (₹)",
                "insert_after": "ef_property_type",
            },
            {
                "fieldname": "ef_budget_max",
                "fieldtype": "Currency",
                "label": "Budget Max (₹)",
                "insert_after": "ef_budget_min",
            },
            {
                "fieldname": "ef_preferred_location",
                "fieldtype": "Data",
                "label": "Preferred Location",
                "insert_after": "ef_budget_max",
                "in_standard_filter": 1,
            },
            {
                "fieldname": "ef_lead_temperature",
                "fieldtype": "Select",
                "label": "Lead Temperature",
                "options": "\nCold\nWarm\nHot",
                "insert_after": "ef_preferred_location",
                "in_list_view": 1,
                "in_standard_filter": 1,
            },
            {
                "fieldname": "ef_next_followup",
                "fieldtype": "Datetime",
                "label": "Next Follow-up",
                "insert_after": "ef_lead_temperature",
            },
            {
                "fieldname": "ef_last_contacted",
                "fieldtype": "Datetime",
                "label": "Last Contacted",
                "insert_after": "ef_next_followup",
                "read_only": 1,
            },
            {
                "fieldname": "ef_call_status",
                "fieldtype": "Select",
                "label": "Call Status",
                "options": "\nCall Pending\nCalled\nCall Failed\nCallback Requested",
                "insert_after": "ef_last_contacted",
                "in_list_view": 1,
            },
        ]
    }

    try:
        create_custom_fields(fields, ignore_validate=True)
        print("[EstateFlow]  → Custom fields added to CRM Lead")
    except Exception as e:
        print(f"[EstateFlow]  ⚠ Custom fields warning (may already exist): {e}")
