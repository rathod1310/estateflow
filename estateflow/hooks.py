from . import __version__ as app_version

app_name = "estateflow"
app_title = "EstateFlow CRM"
app_publisher = "EstateFlow"
app_description = "Mobile-first Real Estate CRM — call bridge, WhatsApp, property sharing, attendance."
app_email = "support@estateflow.in"
app_license = "MIT"
app_version = "1.0.0"
app_icon = "octicon octicon-home"
app_color = "#267a5a"

# ── Fixtures ──────────────────────────────────────────────────────────────────
fixtures = [
    {"dt": "Module Def", "filters": [["app_name", "=", "estateflow"]]},
    {"dt": "EF Message Template", "filters": []},
]

# ── Website routes ─────────────────────────────────────────────────────────────
website_route_rules = [
    {"from_route": "/estateflow",              "to_route": "estateflow/index"},
    {"from_route": "/estateflow/leads",        "to_route": "estateflow/leads/index"},
    {"from_route": "/estateflow/leads/new",    "to_route": "estateflow/leads/new"},
    {"from_route": "/estateflow/leads/<name>", "to_route": "estateflow/leads/detail"},
    {"from_route": "/estateflow/properties",           "to_route": "estateflow/properties/index"},
    {"from_route": "/estateflow/properties/<name>",    "to_route": "estateflow/properties/detail"},
    {"from_route": "/estateflow/follow-ups",   "to_route": "estateflow/follow_ups/index"},
    {"from_route": "/estateflow/attendance",   "to_route": "estateflow/attendance/index"},
    {"from_route": "/estateflow/settings",     "to_route": "estateflow/settings/index"},
    {"from_route": "/share/property/<name>",   "to_route": "share_property"},
]

# ── Jinja helpers ─────────────────────────────────────────────────────────────
jinja = {
    "methods": [
        "estateflow.utils.jinja_helpers.format_inr",
        "estateflow.utils.jinja_helpers.lead_avatar_color",
        "estateflow.utils.jinja_helpers.lead_initials",
    ]
}

# ── Static assets ─────────────────────────────────────────────────────────────
web_include_css = ["/assets/estateflow/css/estateflow.css"]
web_include_js  = ["/assets/estateflow/js/estateflow.js"]

# ── Doc events ────────────────────────────────────────────────────────────────
doc_events = {
    "CRM Lead": {
        "after_insert": "estateflow.api.calls.on_new_lead",
    }
}

# ── Scheduled tasks ───────────────────────────────────────────────────────────
scheduler_events = {
    "hourly": [
        "estateflow.utils.notifications.send_followup_reminders",
    ],
    "daily": [
        "estateflow.utils.notifications.mark_overdue_followups",
    ],
}

# ── Post-install ──────────────────────────────────────────────────────────────
after_install = "estateflow.setup.after_install"

# ── Portal menu entry ─────────────────────────────────────────────────────────
portal_menu_items = [
    {
        "title": "EstateFlow CRM",
        "route": "/estateflow",
        "reference_doctype": "",
        "role": "Sales User",
    },
]
