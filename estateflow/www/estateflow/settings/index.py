import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)
    context.is_admin = frappe.has_role("System Manager")
    context.site_url = frappe.utils.get_url()
