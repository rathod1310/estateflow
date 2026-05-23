import frappe
from frappe.model.document import Document


class EFIntegrationSettings(Document):
    def validate(self):
        if self.twilio_account_sid and not self.twilio_account_sid.startswith("AC"):
            frappe.throw("Twilio Account SID should start with 'AC'")
