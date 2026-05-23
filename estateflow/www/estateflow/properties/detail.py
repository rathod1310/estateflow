import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    prop_name = frappe.form_dict.get("name") or ""
    if not prop_name:
        context.prop = None
        return

    try:
        prop = frappe.get_doc("EF Property", prop_name)
        context.prop = prop
        context.formatted_price = prop.get_formatted_price()
        context.amenities = prop.get_amenities_list()
        context.share_url = prop.get_share_url()
    except frappe.DoesNotExistError:
        context.prop = None
