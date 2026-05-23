frappe.ui.form.on("EF Attendance Log", {
    refresh(frm) {
        if (frm.doc.check_in_latitude && frm.doc.check_in_longitude) {
            const lat = frm.doc.check_in_latitude;
            const lng = frm.doc.check_in_longitude;
            frm.add_custom_button(__("View Check-in Location"), () => {
                window.open(`https://maps.google.com/?q=${lat},${lng}`, "_blank");
            });
        }
        if (frm.doc.check_out_latitude && frm.doc.check_out_longitude) {
            const lat = frm.doc.check_out_latitude;
            const lng = frm.doc.check_out_longitude;
            frm.add_custom_button(__("View Check-out Location"), () => {
                window.open(`https://maps.google.com/?q=${lat},${lng}`, "_blank");
            });
        }
    },
    check_in_time(frm) {
        if (frm.doc.check_in_time && !frm.doc.status) {
            frm.set_value("status", "Present");
        }
    }
});
