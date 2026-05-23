frappe.ui.form.on("EF Follow Up", {
    refresh(frm) {
        if (frm.doc.lead) {
            frm.add_custom_button(__("Open Lead"), () => {
                frappe.set_route("Form", "CRM Lead", frm.doc.lead);
            });
        }
        if (frm.doc.status === "Pending") {
            frm.add_custom_button(__("Mark Sent"), () => {
                frm.set_value("status", "Sent");
                frm.set_value("sent_at", frappe.datetime.now_datetime());
                frm.save();
            }, __("Actions"));
        }
    }
});
