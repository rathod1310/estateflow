/* ═══════════════════════════════════════════════════════
   EstateFlow CRM — estateflow.js
   Shared utilities for all Jinja pages
   ═══════════════════════════════════════════════════════ */

// ── Frappe API wrapper ─────────────────────────────────────────────────────
async function efCall(method, args = {}) {
  try {
    const res = await frappe.call({ method, args });
    return res.message;
  } catch (e) {
    console.error("[EstateFlow] API error:", method, e);
    return null;
  }
}

// ── Toast notifications ────────────────────────────────────────────────────
function efToast(message, type = "info", subtitle = "") {
  const container = document.getElementById("ef-toast-container");
  if (!container) return;

  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  const id = "toast-" + Date.now();
  const el = document.createElement("div");
  el.id = id;
  el.className = `ef-toast ef-toast-${type}`;
  el.innerHTML = `
    <span class="ef-toast-icon">${icons[type] || "ℹ️"}</span>
    <div class="ef-toast-msg">
      ${efEscape(message)}
      ${subtitle ? `<div class="ef-toast-sub">${efEscape(subtitle)}</div>` : ""}
    </div>
    <button class="ef-toast-close" onclick="document.getElementById('${id}').remove()">✕</button>`;
  container.appendChild(el);
  setTimeout(() => { const t = document.getElementById(id); if (t) t.remove(); }, 4500);
}

// ── HTML escape ────────────────────────────────────────────────────────────
function efEscape(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Price formatter ────────────────────────────────────────────────────────
function efPrice(amount) {
  if (!amount) return "—";
  const n = Number(amount);
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)} Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(0)}L`;
  return `₹${n.toLocaleString("en-IN")}`;
}

// ── Relative time ──────────────────────────────────────────────────────────
function efRelTime(dateStr) {
  if (!dateStr) return "—";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(mins / 60);
  const days = Math.floor(hours / 24);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

// ── Time display ───────────────────────────────────────────────────────────
function efTime(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

// ── Duration display ───────────────────────────────────────────────────────
function efDuration(secs) {
  if (!secs) return "";
  const m = Math.floor(secs / 60), s = secs % 60;
  return m ? `${m}m ${s}s` : `${s}s`;
}

// ── Empty state ────────────────────────────────────────────────────────────
function efEmpty(title, subtitle = "") {
  return `<div class="ef-empty">
    <div class="ef-empty-icon">📭</div>
    <div class="ef-empty-title">${efEscape(title)}</div>
    ${subtitle ? `<div class="ef-empty-sub">${efEscape(subtitle)}</div>` : ""}
  </div>`;
}

// ── Avatar helpers ─────────────────────────────────────────────────────────
const AVATAR_COLORS = [
  { bg: "#ede9fe", color: "#6d28d9" },
  { bg: "#dbeafe", color: "#1d4ed8" },
  { bg: "#dcfce7", color: "#15803d" },
  { bg: "#ffedd5", color: "#c2410c" },
  { bg: "#fce7f3", color: "#be185d" },
];

function efAvatarColor(name) {
  const idx = (name || "A").charCodeAt(0) % AVATAR_COLORS.length;
  return AVATAR_COLORS[idx];
}

function efInitials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
}

// ── Lead card renderer (used on dashboard + leads list) ────────────────────
function renderLeadCard(lead) {
  const av = efAvatarColor(lead.lead_name || "");
  const initials = efInitials(lead.lead_name || "");
  const budget = (() => {
    if (!lead.ef_budget_min && !lead.ef_budget_max) return "";
    return `💰 ${efPrice(lead.ef_budget_min)} – ${efPrice(lead.ef_budget_max)}`;
  })();

  const tempEmoji = { Hot: "🔥", Warm: "☀️", Cold: "🧊" }[lead.ef_lead_temperature] || "";
  const tempClass = { Hot: "ef-temp-hot", Warm: "ef-temp-warm", Cold: "ef-temp-cold" }[lead.ef_lead_temperature] || "";
  const statusClass = "ef-status-" + (lead.status || "new").toLowerCase().replace(/\s+/g, "-");

  const nextFollowup = lead.ef_next_followup
    ? `<span class="ef-lead-card-followup">📅 ${new Date(lead.ef_next_followup).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}</span>`
    : "";

  return `
    <a href="/estateflow/leads/${encodeURIComponent(lead.name)}" class="ef-card ef-card-link ef-lead-card-link">
      <div class="ef-lead-card-header">
        <div class="ef-lead-card-avatar" style="background:${av.bg};color:${av.color}">${efEscape(initials)}</div>
        <div class="ef-lead-card-info">
          <p class="ef-lead-card-name">${efEscape(lead.lead_name || "")}</p>
          <p class="ef-lead-card-phone">${efEscape(lead.mobile_no || lead.phone || "")}</p>
        </div>
      </div>
      <div class="ef-lead-card-badges">
        <span class="ef-status-badge ${statusClass}">${efEscape(lead.status || "")}</span>
        ${lead.ef_lead_temperature ? `<span class="ef-temp-badge ${tempClass}">${tempEmoji} ${lead.ef_lead_temperature}</span>` : ""}
        ${lead.source ? `<span class="ef-source-badge">${efEscape(lead.source)}</span>` : ""}
        ${lead.ef_preferred_location ? `<span class="ef-source-badge">📍 ${efEscape(lead.ef_preferred_location)}</span>` : ""}
      </div>
      ${budget ? `<p class="ef-lead-card-budget">${budget}</p>` : ""}
      <div class="ef-lead-card-actions">
        <button class="ef-lead-action-btn ef-action-call-btn"
          onclick="event.preventDefault();event.stopPropagation();quickCall('${encodeURIComponent(lead.name)}','${efEscape(lead.lead_name || '')}')">
          📞 Call
        </button>
        <button class="ef-lead-action-btn ef-action-followup-btn"
          onclick="event.preventDefault();event.stopPropagation();openFollowupSheet('${encodeURIComponent(lead.name)}','${efEscape(lead.lead_name || '')}')">
          💬 Follow-up
        </button>
        <button class="ef-lead-action-btn ef-action-share-btn"
          onclick="event.preventDefault();event.stopPropagation();openShareSheet('${encodeURIComponent(lead.name)}','${efEscape(lead.lead_name || '')}')">
          🔗
        </button>
      </div>
      <div class="ef-lead-card-footer">
        <span class="ef-lead-card-time">${efRelTime(lead.modified)}</span>
        ${nextFollowup}
      </div>
    </a>`;
}

// ── Quick call from list card ──────────────────────────────────────────────
async function quickCall(leadName, leadDisplayName) {
  efToast(`📞 Calling ${decodeURIComponent(leadDisplayName)}…`, "info");
  const r = await efCall("estateflow.api.calls.direct_call_lead", {
    lead_name: decodeURIComponent(leadName)
  });
  if (r?.dry_run) {
    efToast(`[DRY-RUN] Would call ${decodeURIComponent(leadDisplayName)}`, "info",
      "Configure Twilio in Settings for real calls");
  } else if (r?.success) {
    efToast(`✅ Call initiated to ${decodeURIComponent(leadDisplayName)}`, "success");
  } else {
    efToast(r?.error || "Call failed", "error");
  }
}
