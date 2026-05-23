# EstateFlow CRM

A mobile-first Real Estate CRM custom app for ERPNext/Frappe.

Extends ERPNext's CRM Lead doctype with:
- **Instant Call Bridge** — auto-calls agent → bridges to lead (Twilio)
- **One-click WhatsApp/SMS follow-ups** with templates
- **Property sharing** — send property photos & details in one tap
- **Property Inventory** — manage listings with photos, filters, share links
- **Attendance** — GPS-based check-in/check-out for field teams
- **Lead Intake Webhook** — accept leads from 36 Acre, MagicBricks, Facebook Ads, Zapier, etc.
- **Mobile-first UI** — Jinja pages with bottom navigation, bottom sheets, and large tap targets

---

## Installation

### 1. Get the app

```bash
cd /path/to/frappe-bench
bench get-app estateflow https://github.com/your-org/estateflow
```

Or for local development:
```bash
bench get-app estateflow /path/to/estateflow
```

### 2. Install on your site

```bash
bench --site your-site.localhost install-app estateflow
bench --site your-site.localhost migrate
```

This automatically:
- Creates all doctypes (EF Property, EF Call Log, EF Follow Up, EF Attendance Log, etc.)
- Adds custom fields to CRM Lead
- Creates default message templates
- Creates Sales User / Sales Manager / Field Executive roles
- Enables dry-run mode for Twilio and WhatsApp

### 3. Seed sample data (optional but recommended for testing)

```bash
bench --site your-site.localhost execute estateflow.seed.run
```

Creates 10 sample properties, 20 leads, call logs, follow-ups, and attendance records.

### 4. Open the app

```
https://your-site.localhost/estateflow
```

Log in with your ERPNext credentials. The app automatically adapts to your user's role.

---

## Twilio Setup (for real calls and WhatsApp)

By default the app runs in **dry-run mode** — all calls and messages are simulated and logged. No credentials needed to test the UI.

To go live:

1. Sign up at [twilio.com](https://www.twilio.com)
2. Get your **Account SID**, **Auth Token**, and a **Phone Number**
3. For WhatsApp: enable the Twilio WhatsApp Sandbox or get an approved WhatsApp Business number
4. In your Frappe site, go to `/estateflow/settings`
5. Fill in the credentials and uncheck "Dry-Run Mode"
6. Save

### Twilio webhook URLs (configure in Twilio Console)

| Purpose | URL |
|---------|-----|
| Agent call TwiML | `https://your-site/api/method/estateflow.api.calls.twiml_agent` |
| Agent confirm | `https://your-site/api/method/estateflow.api.calls.twiml_agent_confirm` |
| Lead call TwiML | `https://your-site/api/method/estateflow.api.calls.twiml_lead` |
| Call status callback | `https://your-site/api/method/estateflow.api.calls.twilio_status_callback` |

---

## Lead Intake Webhook

External platforms can push leads to:

```
POST https://your-site/api/method/estateflow.api.leads.intake_webhook
Content-Type: application/json
X-Webhook-Secret: your-secret-from-settings
```

### Example payload

```json
{
  "fullName": "Rahul Sharma",
  "phone": "+919999999999",
  "email": "rahul@example.com",
  "source": "36 Acre",
  "propertyType": "Apartment",
  "budgetMin": 7500000,
  "budgetMax": 12000000,
  "preferredLocation": "Gurgaon",
  "notes": "Looking for 3BHK near Golf Course Road"
}
```

### Test with curl

```bash
curl -X POST https://your-site/api/method/estateflow.api.leads.intake_webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret" \
  -d '{
    "fullName": "Test Lead",
    "phone": "+919876543210",
    "source": "Facebook",
    "propertyType": "Apartment",
    "budgetMin": 5000000,
    "budgetMax": 9000000,
    "preferredLocation": "Gurgaon"
  }'
```

### Supported sources

`36 Acre`, `MagicBricks`, `Housing.com`, `Facebook`, `Instagram`, `Website`, `Referral`, `Manual`, `Other`

---

## Platform integrations

### Zapier / Make

1. Use "Webhooks" trigger
2. Set URL to your webhook endpoint
3. Map fields: `fullName`, `phone`, `email`, `source`, `propertyType`, `budgetMin`, `budgetMax`, `preferredLocation`

### Facebook Lead Ads

Use Zapier or Make to bridge Facebook Lead Ads → EstateFlow webhook automatically.

### 36 Acre / MagicBricks

Both platforms support webhook/API forwarding. Set the EstateFlow webhook URL in their lead management settings.

---

## App pages

| URL | Description |
|-----|-------------|
| `/estateflow` | Dashboard — stats, hot leads, quick actions |
| `/estateflow/leads` | Lead list with search, filters, one-click actions |
| `/estateflow/leads/new` | Add lead manually |
| `/estateflow/leads/<name>` | Lead detail — timeline, actions, recommended properties |
| `/estateflow/properties` | Property inventory |
| `/estateflow/properties/<name>` | Property detail + share |
| `/estateflow/follow-ups` | Follow-up history |
| `/estateflow/attendance` | Check-in / check-out + team dashboard |
| `/estateflow/settings` | Integration settings (admin only) |
| `/share/property/<name>` | Public property share page (no login required) |

---

## Custom fields added to CRM Lead

| Field | Type | Description |
|-------|------|-------------|
| `ef_property_type` | Select | Apartment / Villa / Plot / Commercial / Rental |
| `ef_budget_min` | Currency | Minimum budget in ₹ |
| `ef_budget_max` | Currency | Maximum budget in ₹ |
| `ef_preferred_location` | Data | City / area preference |
| `ef_lead_temperature` | Select | Cold / Warm / Hot |
| `ef_next_followup` | Datetime | Scheduled follow-up time |
| `ef_last_contacted` | Datetime | Auto-updated on every call |
| `ef_call_status` | Select | Call Pending / Called / Call Failed / Callback Requested |

---

## New Doctypes

| Doctype | Description |
|---------|-------------|
| `EF Property` | Real estate listing with images, amenities, share link |
| `EF Property Image` | Child table for property photos |
| `EF Call Log` | Call records with Twilio SID, duration, recording URL |
| `EF Follow Up` | WhatsApp/SMS/email log per lead |
| `EF Attendance Log` | GPS check-in/check-out with timestamps |
| `EF Message Template` | Reusable message templates |
| `EF Integration Settings` | Twilio, WhatsApp, webhook, AI credentials |

---

## Development

### Run locally

```bash
bench start
# App available at http://your-site.localhost:8000/estateflow
```

### After changing Python files

```bash
bench restart
```

### After changing JS/CSS

```bash
bench build --app estateflow
# or for watch mode:
bench watch
```

### After changing doctype JSON

```bash
bench --site your-site.localhost migrate
```

### Export fixtures after changes

```bash
bench --site your-site.localhost export-fixtures --app estateflow
```

---

## Dry-run mode

Both Twilio (calls) and WhatsApp (messages) run in dry-run mode by default:

- Calls are simulated — logs are created but no real call is placed
- Messages are logged to the console and saved in EF Follow Up with status "Dry Run"
- All UI flows work identically — you see `[DRY-RUN]` in toast notifications

To disable, fill in Twilio credentials in Settings and uncheck the dry-run checkboxes.

---

## Role access

| Role | Access |
|------|--------|
| System Manager | Full access including Settings |
| Sales Manager | All leads, properties, team attendance |
| Sales User | Assigned leads, properties, own attendance |
| Field Executive | Own attendance, assigned site visits |

---

## Environment requirements

- Frappe v14+ or v15+
- ERPNext v14+ or v15+ with CRM module enabled
- Python 3.10+
- `pip install twilio` (only needed for production calls/messages)
