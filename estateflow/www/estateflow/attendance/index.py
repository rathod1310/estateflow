import frappe
from frappe.utils import today, nowdate, format_date


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    user = frappe.get_doc("User", frappe.session.user)
    name_str = user.full_name or frappe.session.user
    parts = name_str.split()
    context.initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()
    context.full_name = name_str
    context.today = today()
    context.today_display = format_date(today(), "d MMMM yyyy")
    context.is_admin = frappe.has_role("System Manager") or frappe.has_role("HR Manager")
