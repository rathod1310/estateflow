import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class EFCallLog(Document):

    def get_duration_display(self):
        if not self.duration_seconds:
            return "—"
        m, s = divmod(self.duration_seconds, 60)
        return f"{m}m {s}s" if m else f"{s}s"

    @staticmethod
    def create_for_lead(lead_name, agent_email, call_sid=None, dry_run=False):
        doc = frappe.new_doc("EF Call Log")
        doc.lead = lead_name
        doc.agent = agent_email
        doc.call_sid = call_sid or ""
        doc.call_status = "Dry Run" if dry_run else "Initiated"
        doc.dry_run = 1 if dry_run else 0
        doc.started_at = now_datetime()
        doc.insert(ignore_permissions=True)
        return doc
