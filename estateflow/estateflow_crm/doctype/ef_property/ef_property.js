// EF Property — Frappe Desk form JS
frappe.ui.form.on("EF Property", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Copy Share Link"), () => {
                const url = `${window.location.origin}/share/property/${frm.doc.name}`;
                frappe.utils.copy_to_clipboard(url);
                frappe.show_alert({ message: __("Share link copied!"), indicator: "green" });
            });

            frm.add_custom_button(__("Open in EstateFlow"), () => {
                window.open(`/estateflow/properties/${frm.doc.name}`, "_blank");
            });
        }
    },

    price(frm) {
        if (frm.doc.price) {
            const n = frm.doc.price;
            let display = "";
            if (n >= 10000000) display = `₹${(n / 10000000).toFixed(2)} Cr`;
            else if (n >= 100000) display = `₹${(n / 100000).toFixed(0)}L`;
            else display = `₹${n.toLocaleString("en-IN")}`;
            frm.set_intro(`Price: <strong>${display}</strong>`, "blue");
        }
    }
});
