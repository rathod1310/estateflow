"""
estateflow/api/properties.py
"""
import frappe


@frappe.whitelist()
def get_properties(property_type=None, status="Available", location=None, limit=50):
    filters = {}
    if status:
        filters["availability_status"] = status
    if property_type:
        filters["property_type"] = property_type
    if location:
        filters["location"] = ("like", f"%{location}%")

    props = frappe.get_list(
        "EF Property",
        filters=filters,
        fields=[
            "name", "title", "location", "property_type", "price",
            "size_sqft", "bedrooms", "bathrooms", "availability_status",
            "furnishing_status", "developer_name",
        ],
        order_by="modified desc",
        limit=int(limit),
    )
    return props


@frappe.whitelist()
def get_property(property_name):
    prop = frappe.get_doc("EF Property", property_name)
    d = prop.as_dict()
    d["share_url"] = prop.get_share_url()
    d["formatted_price"] = prop.get_formatted_price()
    d["amenities_list"] = prop.get_amenities_list()
    return d


@frappe.whitelist()
def match_properties_for_lead(lead_name):
    """Return properties matching a lead's budget, location, and type."""
    lead = frappe.get_doc("CRM Lead", lead_name)
    budget_min = (lead.get("ef_budget_min") or 0) * 0.8
    budget_max = (lead.get("ef_budget_max") or 99999999999) * 1.2
    prop_type = lead.get("ef_property_type") or ""
    location = lead.get("ef_preferred_location") or ""

    filters = {"availability_status": "Available"}
    if prop_type:
        filters["property_type"] = prop_type

    props = frappe.get_list(
        "EF Property",
        filters=filters,
        fields=[
            "name", "title", "location", "property_type", "price",
            "size_sqft", "bedrooms", "bathrooms", "availability_status",
        ],
        order_by="price asc",
        limit=20,
    )

    # Python-side filter for budget and location
    matched = []
    for p in props:
        price = p.get("price") or 0
        price_ok = (not budget_min or price >= budget_min) and (not budget_max or price <= budget_max)
        loc_ok = not location or location.lower() in (p.get("location") or "").lower()
        if price_ok or loc_ok:
            matched.append(p)

    return matched
