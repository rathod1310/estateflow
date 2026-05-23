frappe.ui.form.on("EF Message Template", {
    refresh(frm) {
        frm.set_intro(
            __("Use {{lead_name}}, {{preferred_location}}, {{property_title}}, {{price}}, {{share_link}} as placeholders."),
            "blue"
        );
    }
});
