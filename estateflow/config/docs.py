from frappe import _


def get_data():
    return [
        {
            "label": _("EstateFlow"),
            "icon": "fa fa-home",
            "items": [
                {
                    "type": "page",
                    "label": _("EstateFlow Dashboard"),
                    "name": "estateflow",
                    "route": "/estateflow",
                    "description": _("Open EstateFlow mobile CRM"),
                },
            ],
        },
        {
            "label": _("Leads & Calls"),
            "icon": "fa fa-phone",
            "items": [
                {
                    "type": "doctype",
                    "name": "CRM Lead",
                    "label": _("CRM Leads"),
                    "description": _("All leads (ERPNext CRM)"),
                },
                {
                    "type": "doctype",
                    "name": "EF Call Log",
                    "label": _("Call Logs"),
                    "description": _("Twilio call bridge logs"),
                },
                {
                    "type": "doctype",
                    "name": "EF Follow Up",
                    "label": _("Follow-ups"),
                    "description": _("WhatsApp / SMS follow-up history"),
                },
            ],
        },
        {
            "label": _("Properties"),
            "icon": "fa fa-building",
            "items": [
                {
                    "type": "doctype",
                    "name": "EF Property",
                    "label": _("Properties"),
                    "description": _("Real estate inventory"),
                },
            ],
        },
        {
            "label": _("Team"),
            "icon": "fa fa-users",
            "items": [
                {
                    "type": "doctype",
                    "name": "EF Attendance Log",
                    "label": _("Attendance"),
                    "description": _("GPS check-in / check-out"),
                },
                {
                    "type": "doctype",
                    "name": "EF Message Template",
                    "label": _("Message Templates"),
                    "description": _("WhatsApp / SMS templates"),
                },
            ],
        },
        {
            "label": _("Settings"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "EF Integration Settings",
                    "label": _("Integration Settings"),
                    "description": _("Twilio, WhatsApp, Webhook config"),
                },
            ],
        },
    ]
