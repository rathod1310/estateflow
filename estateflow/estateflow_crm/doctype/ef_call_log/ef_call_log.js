frappe.ui.form.on("EF Call Log", {
    refresh(frm) {
        if (frm.doc.recording_url) {
            frm.add_custom_button(__("▶ Play Recording"), () => {
                window.open(frm.doc.recording_url, "_blank");
            });
        }
        if (frm.doc.lead) {
            frm.add_custom_button(__("Open Lead"), () => {
                frappe.set_route("Form", "CRM Lead", frm.doc.lead);
            });
        }
        // Duration display
        if (frm.doc.duration_seconds) {
            const m = Math.floor(frm.doc.duration_seconds / 60);
            const s = frm.doc.duration_seconds % 60;
            frm.set_intro(`Duration: ${m}m ${s}s`, "blue");
        }
    }
});
