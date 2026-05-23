import frappe
from frappe.utils import now_datetime


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    hour = now_datetime().hour
    if hour < 12:
        context.greeting = "morning"
    elif hour < 17:
        context.greeting = "afternoon"
    else:
        context.greeting = "evening"
