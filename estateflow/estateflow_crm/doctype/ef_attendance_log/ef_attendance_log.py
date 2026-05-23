import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class EFAttendanceLog(Document):

    def validate(self):
        if self.check_out_time and self.check_in_time:
            if self.check_out_time < self.check_in_time:
                frappe.throw("Check-out time cannot be before check-in time")

    def get_duration_display(self):
        if not self.check_in_time or not self.check_out_time:
            return "—"
        from frappe.utils import time_diff_in_seconds
        secs = time_diff_in_seconds(self.check_out_time, self.check_in_time)
        hours, rem = divmod(int(secs), 3600)
        mins = rem // 60
        return f"{hours}h {mins}m"

    @staticmethod
    def get_todays_record(user_email):
        records = frappe.get_list(
            "EF Attendance Log",
            filters={"employee_user": user_email, "attendance_date": today()},
            fields=["name", "check_in_time", "check_out_time", "status"],
            limit=1,
        )
        return records[0] if records else None
