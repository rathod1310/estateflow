frappe.ui.form.on("EF Integration Settings", {
    refresh(frm) {
        const isDry = frm.doc.twilio_dry_run || frm.doc.whatsapp_dry_run;
        if (isDry) {
            frm.set_intro(
                "🧪 Dry-Run Mode is active. Calls and messages are simulated — no real Twilio API calls are made.",
                "orange"
            );
        } else {
            frm.set_intro("✅ Live mode active. Real calls and messages will be placed.", "green");
        }

        frm.add_custom_button(__("Copy Webhook URL"), () => {
            const url = `${window.location.origin}/api/method/estateflow.api.leads.intake_webhook`;
            frappe.utils.copy_to_clipboard(url);
            frappe.show_alert({ message: __("Webhook URL copied!"), indicator: "green" });
        });

        frm.add_custom_button(__("Open EstateFlow"), () => {
            window.open("/estateflow", "_blank");
        });
    },
    twilio_dry_run(frm) { frm.trigger("refresh"); },
    whatsapp_dry_run(frm) { frm.trigger("refresh"); }
});
