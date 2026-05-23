import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    lead_name = frappe.form_dict.get("name") or ""
    if not lead_name:
        context.lead = None
        return

    try:
        lead = frappe.get_doc("CRM Lead", lead_name)
        context.lead = lead
    except frappe.DoesNotExistError:
        context.lead = None
        return

    # Initials + avatar color
    name_str = lead.lead_name or lead.first_name or "?"
    parts = name_str.split()
    context.initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()

    colors = ["#a78bfa", "#60a5fa", "#34d399", "#f97316", "#f472b6"]
    context.avatar_color = colors[ord(name_str[0]) % len(colors)]

    # Budget range display
    lo = lead.get("ef_budget_min")
    hi = lead.get("ef_budget_max")

    def fmt(n):
        if not n:
            return None
        lakh = 100000
        crore = 10000000
        if n >= crore:
            return f"₹{n/crore:.1f} Cr"
        return f"₹{n/lakh:.0f}L"

    if lo and hi:
        context.budget_range = f"{fmt(lo)} – {fmt(hi)}"
    elif lo:
        context.budget_range = f"From {fmt(lo)}"
    elif hi:
        context.budget_range = f"Up to {fmt(hi)}"
    else:
        context.budget_range = ""
