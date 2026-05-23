"""
EstateFlow Seed Data Script
============================
Run with:
    bench --site your-site.localhost execute estateflow.seed.run

Creates:
  - 10 sample EF Properties
  - 20 sample CRM Leads with EstateFlow custom fields
  - Sample call logs and follow-ups
  - Sample attendance records
"""

import frappe
from frappe.utils import now_datetime, add_days, today, getdate
import random


PROPERTY_SAMPLES = [
    {
        "title": "Luxury 3BHK in Golf Course Road",
        "location": "Golf Course Road, Gurgaon",
        "preferred_area": "Gurgaon",
        "property_type": "Apartment",
        "price": 12500000,
        "size_sqft": 1850,
        "bedrooms": 3,
        "bathrooms": 3,
        "floor": 8,
        "furnishing_status": "Semi-Furnished",
        "availability_status": "Available",
        "developer_name": "DLF Ltd",
        "description": "Spacious 3BHK apartment with stunning views of the golf course. Modern amenities, 24x7 security, and excellent connectivity.",
        "amenities": "Gym, Swimming Pool, Parking, Security, Club House, Garden",
    },
    {
        "title": "Premium 2BHK Apartment Sector 62",
        "location": "Sector 62, Noida",
        "preferred_area": "Noida",
        "property_type": "Apartment",
        "price": 6800000,
        "size_sqft": 1200,
        "bedrooms": 2,
        "bathrooms": 2,
        "floor": 4,
        "furnishing_status": "Unfurnished",
        "availability_status": "Available",
        "developer_name": "Supertech Ltd",
        "description": "Well-connected 2BHK in the heart of Noida's IT hub. Walking distance to metro station.",
        "amenities": "Gym, Parking, Security, Power Backup",
    },
    {
        "title": "Independent Villa Whitefield",
        "location": "Whitefield, Bangalore",
        "preferred_area": "Bangalore",
        "property_type": "Villa",
        "price": 28000000,
        "size_sqft": 3200,
        "bedrooms": 4,
        "bathrooms": 4,
        "furnishing_status": "Furnished",
        "availability_status": "Available",
        "developer_name": "Prestige Group",
        "description": "Stunning independent villa in the premium Whitefield locality. Private garden and terrace.",
        "amenities": "Private Garden, Terrace, Parking x2, Security, Smart Home",
    },
    {
        "title": "Commercial Office Space Cyber City",
        "location": "Cyber City, Gurgaon",
        "preferred_area": "Gurgaon",
        "property_type": "Commercial",
        "price": 45000000,
        "size_sqft": 5000,
        "availability_status": "Available",
        "developer_name": "Hines India",
        "description": "Premium Grade-A office space in the most sought-after business district.",
        "amenities": "24x7 Access, Cafeteria, Conference Rooms, Valet Parking",
    },
    {
        "title": "Affordable Plot Sector 150 Noida",
        "location": "Sector 150, Noida",
        "preferred_area": "Noida",
        "property_type": "Plot",
        "price": 8500000,
        "size_sqft": 1000,
        "availability_status": "Available",
        "description": "Well-located plot in rapidly developing Sector 150. Near expressway and proposed metro.",
        "amenities": "Corner Plot, Wide Road Facing, Electricity, Water Supply",
    },
    {
        "title": "Studio Apartment for Rent Koramangala",
        "location": "Koramangala, Bangalore",
        "preferred_area": "Bangalore",
        "property_type": "Rental",
        "price": 25000,
        "size_sqft": 450,
        "bedrooms": 1,
        "bathrooms": 1,
        "furnishing_status": "Furnished",
        "availability_status": "Available",
        "description": "Fully furnished studio apartment in the heart of Koramangala. Ideal for working professionals.",
        "amenities": "WiFi Ready, AC, Washing Machine, Parking",
    },
    {
        "title": "4BHK Penthouse Bandra West",
        "location": "Bandra West, Mumbai",
        "preferred_area": "Mumbai",
        "property_type": "Apartment",
        "price": 95000000,
        "size_sqft": 4500,
        "bedrooms": 4,
        "bathrooms": 5,
        "floor": 22,
        "furnishing_status": "Furnished",
        "availability_status": "Available",
        "developer_name": "Lodha Group",
        "description": "Ultra-luxury penthouse with sea views. Private terrace, smart home automation, concierge service.",
        "amenities": "Sea View, Terrace, Smart Home, Concierge, Valet, Gym, Pool",
    },
    {
        "title": "3BHK Villa Sarjapur Road",
        "location": "Sarjapur Road, Bangalore",
        "preferred_area": "Bangalore",
        "property_type": "Villa",
        "price": 18500000,
        "size_sqft": 2400,
        "bedrooms": 3,
        "bathrooms": 3,
        "furnishing_status": "Semi-Furnished",
        "availability_status": "Hold",
        "developer_name": "Brigade Group",
        "description": "Beautiful villa in gated community. Close to tech parks and international schools.",
        "amenities": "Club House, Pool, Gym, Garden, Jogging Track, Security",
    },
    {
        "title": "2BHK Apartment Powai Mumbai",
        "location": "Powai, Mumbai",
        "preferred_area": "Mumbai",
        "property_type": "Apartment",
        "price": 14500000,
        "size_sqft": 1100,
        "bedrooms": 2,
        "bathrooms": 2,
        "floor": 6,
        "furnishing_status": "Unfurnished",
        "availability_status": "Available",
        "developer_name": "Hiranandani Group",
        "description": "Ready-to-move 2BHK in Hiranandani Estate. Lake view, excellent connectivity.",
        "amenities": "Lake View, Gym, Pool, Security, Power Backup, Parking",
    },
    {
        "title": "Commercial Shop Ground Floor Connaught Place",
        "location": "Connaught Place, Delhi",
        "preferred_area": "Delhi",
        "property_type": "Commercial",
        "price": 35000000,
        "size_sqft": 800,
        "floor": 0,
        "availability_status": "Available",
        "description": "Prime commercial shop in Connaught Place. High footfall, excellent visibility.",
        "amenities": "Corner Shop, Wide Frontage, High Footfall Area",
    },
]

LEAD_SAMPLES = [
    {"lead_name": "Rahul Sharma", "mobile_no": "+919876543210", "source": "36 Acre", "ef_property_type": "Apartment", "ef_budget_min": 7500000, "ef_budget_max": 12000000, "ef_preferred_location": "Gurgaon", "status": "New", "ef_lead_temperature": "Hot", "notes": "Looking for 3BHK near Golf Course Road. Urgent requirement."},
    {"lead_name": "Priya Patel", "mobile_no": "+919765432109", "source": "MagicBricks", "ef_property_type": "Villa", "ef_budget_min": 15000000, "ef_budget_max": 25000000, "ef_preferred_location": "Bangalore", "status": "Contacted", "ef_lead_temperature": "Warm"},
    {"lead_name": "Amit Kumar", "mobile_no": "+919654321098", "source": "Facebook", "ef_property_type": "Apartment", "ef_budget_min": 5000000, "ef_budget_max": 8000000, "ef_preferred_location": "Noida", "status": "Interested", "ef_lead_temperature": "Hot"},
    {"lead_name": "Sunita Reddy", "mobile_no": "+919543210987", "source": "Housing.com", "ef_property_type": "Plot", "ef_budget_min": 6000000, "ef_budget_max": 10000000, "ef_preferred_location": "Hyderabad", "status": "Site Visit Scheduled", "ef_lead_temperature": "Warm"},
    {"lead_name": "Vikram Singh", "mobile_no": "+919432109876", "source": "Instagram", "ef_property_type": "Commercial", "ef_budget_min": 20000000, "ef_budget_max": 50000000, "ef_preferred_location": "Delhi", "status": "Negotiation", "ef_lead_temperature": "Hot"},
    {"lead_name": "Neha Gupta", "mobile_no": "+919321098765", "source": "Website", "ef_property_type": "Rental", "ef_budget_min": 20000, "ef_budget_max": 35000, "ef_preferred_location": "Bangalore", "status": "New", "ef_lead_temperature": "Warm"},
    {"lead_name": "Rajan Mehta", "mobile_no": "+919210987654", "source": "Referral", "ef_property_type": "Apartment", "ef_budget_min": 10000000, "ef_budget_max": 18000000, "ef_preferred_location": "Mumbai", "status": "Contacted", "ef_lead_temperature": "Cold"},
    {"lead_name": "Ananya Iyer", "mobile_no": "+919109876543", "source": "36 Acre", "ef_property_type": "Villa", "ef_budget_min": 25000000, "ef_budget_max": 40000000, "ef_preferred_location": "Chennai", "status": "New", "ef_lead_temperature": "Hot"},
    {"lead_name": "Deepak Joshi", "mobile_no": "+919098765432", "source": "MagicBricks", "ef_property_type": "Apartment", "ef_budget_min": 4000000, "ef_budget_max": 7000000, "ef_preferred_location": "Pune", "status": "Lost", "ef_lead_temperature": "Cold", "notes": "Budget constraints. Follow up after 3 months."},
    {"lead_name": "Kavita Nair", "mobile_no": "+918987654321", "source": "Facebook", "ef_property_type": "Apartment", "ef_budget_min": 8000000, "ef_budget_max": 14000000, "ef_preferred_location": "Gurgaon", "status": "Interested", "ef_lead_temperature": "Warm"},
    {"lead_name": "Sanjay Verma", "mobile_no": "+918876543210", "source": "Manual", "ef_property_type": "Plot", "ef_budget_min": 5000000, "ef_budget_max": 9000000, "ef_preferred_location": "Faridabad", "status": "New", "ef_lead_temperature": "Cold"},
    {"lead_name": "Pooja Agarwal", "mobile_no": "+918765432109", "source": "Housing.com", "ef_property_type": "Apartment", "ef_budget_min": 6500000, "ef_budget_max": 11000000, "ef_preferred_location": "Noida", "status": "Contacted", "ef_lead_temperature": "Warm"},
    {"lead_name": "Manoj Tiwari", "mobile_no": "+918654321098", "source": "Instagram", "ef_property_type": "Commercial", "ef_budget_min": 12000000, "ef_budget_max": 20000000, "ef_preferred_location": "Gurgaon", "status": "Site Visit Scheduled", "ef_lead_temperature": "Hot"},
    {"lead_name": "Rekha Sharma", "mobile_no": "+918543210987", "source": "Website", "ef_property_type": "Villa", "ef_budget_min": 18000000, "ef_budget_max": 30000000, "ef_preferred_location": "Hyderabad", "status": "Negotiation", "ef_lead_temperature": "Hot"},
    {"lead_name": "Arun Pillai", "mobile_no": "+918432109876", "source": "Referral", "ef_property_type": "Apartment", "ef_budget_min": 9000000, "ef_budget_max": 15000000, "ef_preferred_location": "Bangalore", "status": "Won", "ef_lead_temperature": "Hot", "notes": "Deal closed! 3BHK in Whitefield."},
    {"lead_name": "Meena Krishnan", "mobile_no": "+918321098765", "source": "36 Acre", "ef_property_type": "Rental", "ef_budget_min": 15000, "ef_budget_max": 25000, "ef_preferred_location": "Chennai", "status": "New", "ef_lead_temperature": "Warm"},
    {"lead_name": "Suresh Yadav", "mobile_no": "+918210987654", "source": "MagicBricks", "ef_property_type": "Apartment", "ef_budget_min": 3500000, "ef_budget_max": 6000000, "ef_preferred_location": "Lucknow", "status": "Not Responding", "ef_lead_temperature": "Cold"},
    {"lead_name": "Divya Kapoor", "mobile_no": "+918109876543", "source": "Facebook", "ef_property_type": "Apartment", "ef_budget_min": 11000000, "ef_budget_max": 17000000, "ef_preferred_location": "Mumbai", "status": "Interested", "ef_lead_temperature": "Warm"},
    {"lead_name": "Ramesh Choudhury", "mobile_no": "+917987654321", "source": "Manual", "ef_property_type": "Plot", "ef_budget_min": 8000000, "ef_budget_max": 12000000, "ef_preferred_location": "Jaipur", "status": "New", "ef_lead_temperature": "Cold"},
    {"lead_name": "Lata Bhatt", "mobile_no": "+917876543210", "source": "Website", "ef_property_type": "Villa", "ef_budget_min": 22000000, "ef_budget_max": 35000000, "ef_preferred_location": "Pune", "status": "Contacted", "ef_lead_temperature": "Warm"},
]


def run():
    frappe.set_user("Administrator")
    print("[EstateFlow Seed] Starting...")

    props = _seed_properties()
    leads = _seed_leads()
    _seed_call_logs(leads)
    _seed_follow_ups(leads)
    _seed_attendance()

    frappe.db.commit()
    print(f"[EstateFlow Seed] ✅ Done — {len(props)} properties, {len(leads)} leads seeded.")


def _seed_properties():
    created = []
    for p in PROPERTY_SAMPLES:
        if frappe.db.exists("EF Property", {"title": p["title"]}):
            print(f"  [skip] Property exists: {p['title']}")
            continue
        doc = frappe.new_doc("EF Property")
        doc.update(p)
        doc.insert(ignore_permissions=True)
        created.append(doc.name)
        print(f"  [+] Property: {p['title']}")
    return created


def _seed_leads():
    created = []
    agents = _get_agent_emails()
    for i, l in enumerate(LEAD_SAMPLES):
        if frappe.db.exists("CRM Lead", {"mobile_no": l["mobile_no"]}):
            existing = frappe.db.get_value("CRM Lead", {"mobile_no": l["mobile_no"]}, "name")
            created.append(existing)
            print(f"  [skip] Lead exists: {l['lead_name']}")
            continue
        parts = l["lead_name"].split(" ", 1)
        doc = frappe.new_doc("CRM Lead")
        doc.first_name = parts[0]
        doc.last_name = parts[1] if len(parts) > 1 else ""
        doc.lead_name = l["lead_name"]
        doc.mobile_no = l["mobile_no"]
        doc.source = l.get("source", "Manual")
        doc.status = l.get("status", "New")
        doc.notes = l.get("notes", "")
        doc.lead_owner = agents[i % len(agents)] if agents else ""
        # EstateFlow custom fields
        doc.ef_property_type = l.get("ef_property_type", "")
        doc.ef_budget_min = l.get("ef_budget_min", 0)
        doc.ef_budget_max = l.get("ef_budget_max", 0)
        doc.ef_preferred_location = l.get("ef_preferred_location", "")
        doc.ef_lead_temperature = l.get("ef_lead_temperature", "Warm")
        doc.ef_call_status = "Called" if l.get("status") not in ("New",) else "Call Pending"
        doc.flags.ignore_mandatory = True
        doc.insert(ignore_permissions=True, ignore_links=True)
        created.append(doc.name)
        print(f"  [+] Lead: {l['lead_name']}")
    return created


def _seed_call_logs(lead_names):
    for i, lead_name in enumerate(lead_names[:10]):
        if frappe.db.exists("EF Call Log", {"lead": lead_name}):
            continue
        agents = _get_agent_emails()
        if not agents:
            break
        doc = frappe.new_doc("EF Call Log")
        doc.lead = lead_name
        doc.agent = agents[i % len(agents)]
        doc.call_status = random.choice(["Completed", "No Answer", "Completed", "Completed"])
        doc.dry_run = 1
        doc.started_at = add_days(now_datetime(), -random.randint(0, 7))
        doc.duration_seconds = random.randint(45, 480) if doc.call_status == "Completed" else 0
        doc.outcome = random.choice(["Interested", "Callback Requested", "Connected", "Not Answered"])
        doc.insert(ignore_permissions=True)
    print("  [+] Call logs seeded")


def _seed_follow_ups(lead_names):
    agents = _get_agent_emails()
    templates = ["Quick Check-in", "Invite for Call", "New Options Available"]
    for i, lead_name in enumerate(lead_names[:12]):
        if frappe.db.exists("EF Follow Up", {"lead": lead_name}):
            continue
        doc = frappe.new_doc("EF Follow Up")
        doc.lead = lead_name
        doc.agent = agents[i % len(agents)] if agents else "Administrator"
        doc.channel = "WhatsApp"
        doc.template = templates[i % len(templates)]
        doc.status = random.choice(["Sent", "Sent", "Dry Run", "Pending"])
        doc.dry_run = 1 if doc.status == "Dry Run" else 0
        doc.message = f"Hi, following up on your property inquiry. Please let us know how we can help!"
        doc.sent_at = add_days(now_datetime(), -random.randint(0, 5)) if doc.status in ("Sent", "Dry Run") else None
        doc.insert(ignore_permissions=True)
    print("  [+] Follow-ups seeded")


def _seed_attendance():
    agents = _get_agent_emails()
    if not agents:
        return
    for i, agent in enumerate(agents[:3]):
        att_date = today()
        if frappe.db.exists("EF Attendance Log", {"employee_user": agent, "attendance_date": att_date}):
            continue
        doc = frappe.new_doc("EF Attendance Log")
        doc.employee_user = agent
        doc.attendance_date = att_date
        doc.status = "Present"
        doc.check_in_time = frappe.utils.get_datetime(f"{att_date} 09:{10+i*5}:00")
        doc.check_in_latitude = 28.4595 + random.uniform(-0.01, 0.01)
        doc.check_in_longitude = 77.0266 + random.uniform(-0.01, 0.01)
        if i < 2:  # Two agents have checked out
            doc.check_out_time = frappe.utils.get_datetime(f"{att_date} 18:{15+i*5}:00")
        doc.insert(ignore_permissions=True)
    print("  [+] Attendance records seeded")


def _get_agent_emails():
    users = frappe.get_list(
        "Has Role",
        filters={"role": "Sales User", "parenttype": "User"},
        fields=["parent"],
        as_list=True,
    )
    emails = [u[0] for u in users if u[0] != "Administrator"]
    if not emails:
        # Fallback to Administrator
        emails = ["Administrator"]
    return emails
