"""
estateflow/utils/notifications.py
Scheduled task handlers.
"""
import frappe
from frappe.utils import now_datetime, today


def send_followup_reminders():
    """
    Hourly: find pending follow-ups due now and notify the assigned agent
    via Frappe's built-in notification system.
    """
    overdue = frappe.get_list(
        "EF Follow Up",
        filters={
            "status": "Pending",
            "scheduled_at": ("<=", now_datetime()),
        },
        fields=["name", "lead", "lead_name_display", "agent", "channel", "scheduled_at"],
        limit=50,
    )

    for fu in overdue:
        try:
            if not fu.agent:
                continue
            frappe.publish_realtime(
                event="estateflow_notification",
                message={
                    "type": "followup_due",
                    "title": "Follow-up Due",
                    "body": f"Follow-up due for {fu.lead_name_display or fu.lead} via {fu.channel}",
                    "lead": fu.lead,
                    "follow_up": fu.name,
                },
                user=fu.agent,
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"EstateFlow: followup reminder {fu.name}")


def mark_overdue_followups():
    """
    Daily: log stats — extend this for daily digest emails.
    """
    hot_no_contact = frappe.db.count(
        "CRM Lead",
        {
            "ef_lead_temperature": "Hot",
            "ef_call_status": "Call Pending",
        },
    )
    if hot_no_contact:
        frappe.log_error(
            f"{hot_no_contact} hot leads have not been called yet today.",
            "EstateFlow Daily: Uncalled Hot Leads",
        )
