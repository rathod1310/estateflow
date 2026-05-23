"""
estateflow/api/attendance.py
"""
import frappe
from frappe.utils import today, now_datetime


@frappe.whitelist()
def check_in(latitude=None, longitude=None, notes=None):
    """Mark check-in for logged-in user."""
    user = frappe.session.user
    existing = _get_today_record(user)

    if existing and existing.get("check_in_time"):
        frappe.throw("You have already checked in today.")

    if existing:
        doc = frappe.get_doc("EF Attendance Log", existing["name"])
    else:
        doc = frappe.new_doc("EF Attendance Log")
        doc.employee_user = user
        doc.attendance_date = today()

    doc.check_in_time = now_datetime()
    doc.check_in_latitude = float(latitude) if latitude else None
    doc.check_in_longitude = float(longitude) if longitude else None
    doc.status = "Present"
    if notes:
        doc.notes = notes

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "record": doc.name, "check_in_time": str(doc.check_in_time)}


@frappe.whitelist()
def check_out(latitude=None, longitude=None, notes=None):
    """Mark check-out for logged-in user."""
    user = frappe.session.user
    existing = _get_today_record(user)

    if not existing or not existing.get("check_in_time"):
        frappe.throw("You have not checked in today.")
    if existing.get("check_out_time"):
        frappe.throw("You have already checked out today.")

    doc = frappe.get_doc("EF Attendance Log", existing["name"])
    doc.check_out_time = now_datetime()
    doc.check_out_latitude = float(latitude) if latitude else None
    doc.check_out_longitude = float(longitude) if longitude else None
    if notes:
        doc.notes = (doc.notes or "") + "\nCheck-out: " + notes
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "record": doc.name, "check_out_time": str(doc.check_out_time)}


@frappe.whitelist()
def get_my_status():
    """Return today's attendance status for logged-in user."""
    user = frappe.session.user
    record = _get_today_record(user)
    return {
        "checked_in": bool(record and record.get("check_in_time")),
        "checked_out": bool(record and record.get("check_out_time")),
        "record": record,
    }


@frappe.whitelist()
def get_team_attendance(date=None):
    """Admin: return full team attendance for a date."""
    target_date = date or today()
    records = frappe.get_list(
        "EF Attendance Log",
        filters={"attendance_date": target_date},
        fields=[
            "name", "employee_user", "attendance_date", "status",
            "check_in_time", "check_out_time",
            "check_in_latitude", "check_in_longitude",
        ],
        order_by="check_in_time asc",
    )
    # Enrich with user full name
    for r in records:
        r["full_name"] = frappe.db.get_value("User", r["employee_user"], "full_name")
    return records


def _get_today_record(user):
    records = frappe.get_list(
        "EF Attendance Log",
        filters={"employee_user": user, "attendance_date": today()},
        fields=["name", "check_in_time", "check_out_time", "status"],
        limit=1,
    )
    return records[0] if records else None
