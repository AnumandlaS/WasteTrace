// WasteTrace Frontend Logic

let incidents = [];
let facilities = [];
let homeMap, incidentMap, resultsMap;
let incidentMarker;
let resultsMarkers = [];
let homeMarkers = [];

const $ = (id) => document.getElementById(id);

async function getJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

function setStatus(text) {
  const el = $("status");
  if (el) el.textContent = text;
}

// ── Screen Navigation ────────────────────────────────
window.showScreen = function (screenName) {
  document.querySelectorAll(".screen").forEach((s) => s.classList.remove("active"));
  const target = $(`screen-${screenName}`);
  if (target) {
    target.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Invalidate map sizes when screens become visible
  setTimeout(() => {
    if (screenName === "home" && homeMap) homeMap.invalidateSize();
    if (screenName === "incident" && incidentMap) incidentMap.invalidateSize();
    if (screenName === "results" && resultsMap) resultsMap.invalidateSize();
  }, 100);
};

// ── Evidence Modal Functions ─────────────────────────
window.closeEvidence = function (event) {
  if (event && event.target !== event.currentTarget) return;
  const modal = $("evidenceModal");
  if (modal) modal.classList.remove("active");
};

window.viewEvidence = async function (companyId) {
  const modal = $("evidenceModal");
  const content = $("evidenceContent");
  if (!modal || !content) return;

  content.innerHTML = `<div class="loading-content"><div class="spinner"></div><p>Loading company evidence records...</p></div>`;
  modal.classList.add("active");

  try {
    const data = await getJSON(`/api/companies/${encodeURIComponent(companyId)}/evidence`);
    
    let evHtml = data.evidence.map(ev => `
      <div class="evidence-item glass-card" style="margin-bottom:12px; padding:12px; border-radius:8px;">
        <div style="display:flex; justify-between; align-items:center;">
          <strong style="color:var(--accent-orange, #ff6b35);">${ev.evidence_type.replace(/_/g, ' ').toUpperCase()}</strong>
          <span style="font-size:0.8rem; color:#888;">${ev.date}</span>
        </div>
        <p style="margin:6px 0; font-size:0.9rem;">${ev.description}</p>
        <div style="font-size:0.8rem; color:#aaa;">Source: ${ev.source_agency} | Severity: <strong>${ev.severity}</strong></div>
      </div>
    `).join("");

    if (!evHtml) {
      evHtml = "<p>No regulatory violation evidence records found on file for this facility.</p>";
    }

    let wasteHtml = data.waste_profiles.map(wp => `
      <span style="display:inline-block; background:rgba(255,255,255,0.1); padding:4px 8px; border-radius:4px; margin:2px; font-size:0.85rem;">
        ${wp.waste_type} (${wp.typical_quantity_pm} t/month)
      </span>
    `).join("");

    content.innerHTML = `
      <h2 style="margin-top:0;">${data.company_name}</h2>
      <p style="color:#aaa; font-size:0.9rem;">Facility ID: <code>${data.company_id}</code></p>

      <h4 style="margin:16px 0 8px 0;">Permitted Waste Stream Profiles</h4>
      <div>${wasteHtml || "None registered"}</div>

      <h4 style="margin:16px 0 8px 0;">Regulatory & Compliance Evidence History</h4>
      <div>${evHtml}</div>
    `;
  } catch (err) {
    console.error(err);
    content.innerHTML = `<p style="color:#ff4d4d;">Failed to load evidence records.</p>`;
  }
};

// ── Seeded Case Quick Demo ───────────────────────────
window.loadSeededCase = async function () {
  showScreen("incident");
  if (incidents.length > 0) {
    selectIncident(incidents[0].incident_id);
    $("investigate").click();
  }
};

// ── Map Helpers ──────────────────────────────────────
function selectIncident(id) {
  const x = incidents.find((i) => i.incident_id === id);
  if (!x) return;
  $("lat").value = x.latitude;
  $("lon").value = x.longitude;
  $("date").value = x.date;
  $("qty").value = x.quantity_tonnes;
  $("wasteType").value = x.waste_type;
  if ($("description")) $("description").value = x.description || "";
  updateIncidentMap();
}

function updateIncidentMap() {
  const lat = Number($("lat").value);
  const lon = Number($("lon").value);
  if (!incidentMap || !Number.isFinite(lat) || !Number.isFinite(lon)) return;
  incidentMap.setView([lat, lon], 14);
  if (incidentMarker) incidentMap.removeLayer(incidentMarker);
  incidentMarker = L.marker([lat, lon], { draggable: true })
    .addTo(incidentMap)
    .bindPopup("Waste incident location")
    .openPopup();

  incidentMarker.on("dragend", function (e) {
    const pos = e.target.getLatLng();
    $("lat").value = pos.lat.toFixed(6);
    $("lon").value = pos.lng.toFixed(6);
  });
}

function bar(label, value) {
  const pct = Math.min(100, Math.max(0, value));
  return `
    <div class="barrow" style="margin-bottom:6px;">
      <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:2px;">
        <span>${label}</span>
        <span>${value.toFixed(1)}/100</span>
      </div>
      <div class="bartrack" style="background:rgba(255,255,255,0.1); height:6px; border-radius:3px; overflow:hidden;">
        <div class="barfill" style="width:${pct}%; height:100%; background:linear-gradient(90deg, #ff6b35, #f7c548); border-radius:3px;"></div>
      </div>
    </div>`;
}

// ── Render Results ───────────────────────────────────
function renderResults(data) {
  // 1. Summary Bar
  const summaryBox = $("resultsSummary");
  if (summaryBox) {
    const top = data.candidates[0];
    summaryBox.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px; padding:16px;">
        <div>
          <span style="font-size:0.85rem; color:#888; text-transform:uppercase;">Top Potential Source</span>
          <h3 style="margin:4px 0 0 0; font-size:1.4rem;">${top ? top.facility.company_name : "None identified"}</h3>
        </div>
        <div>
          <span style="font-size:0.85rem; color:#888; text-transform:uppercase;">Highest Attribution Score</span>
          <div style="font-size:1.4rem; font-weight:800; color:var(--accent-orange, #ff6b35);">${top ? top.score.toFixed(1) : 0}/100</div>
        </div>
        <div>
          <span style="font-size:0.85rem; color:#888; text-transform:uppercase;">Evaluated Facilities</span>
          <div style="font-size:1.4rem; font-weight:700;">${data.candidates.length} candidate facilities</div>
        </div>
      </div>
    `;
  }

  // 2. Narrative & Report Link
  if ($("narrative")) $("narrative").textContent = data.narrative;
  if ($("reportLink")) $("reportLink").href = data.report_url;

  // 3. Render Candidate Cards
  const box = $("candidateList");
  box.innerHTML = "";

  data.candidates.forEach((c, idx) => {
    const f = c.facility;
    const badgeClass = c.score >= 70 ? "high" : c.score >= 40 ? "med" : "low";
    const div = document.createElement("div");
    div.className = "candidate-card glass-card";
    div.style.marginBottom = "16px";
    div.style.padding = "20px";
    div.style.borderRadius = "12px";

    div.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
        <div>
          <span style="font-size:0.8rem; color:#888;">#${idx + 1} Candidate</span>
          <h3 style="margin:2px 0 4px 0;">${f.company_name}</h3>
          <span style="font-size:0.85rem; color:#aaa;">${f.industry} · ${c.distance_km.toFixed(2)} km away</span>
        </div>
        <div style="text-align:right;">
          <div style="font-size:1.6rem; font-weight:800; color:${c.score >= 70 ? '#ff6b35' : c.score >= 40 ? '#f7c548' : '#2ec4b6'};">${c.score.toFixed(1)}</div>
          <span style="font-size:0.75rem; text-transform:uppercase; font-weight:600;">Score</span>
        </div>
      </div>

      <div style="margin-bottom:12px;">
        ${bar("Spatial Proximity", c.components.spatial)}
        ${bar("Waste Compatibility", c.components.waste)}
        ${bar("Capacity Match", c.components.capacity)}
        ${bar("Regulatory Violation Record", c.components.regulatory)}
      </div>

      <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; font-size:0.9rem; margin-bottom:12px;">
        <strong>Attribution Rationale:</strong> ${c.waste_match}.
        <br><span style="color:#aaa; font-size:0.85rem;">${f.source_note || ""}</span>
      </div>

      <div style="display:flex; gap:12px;">
        <button class="btn btn-glass" style="padding:6px 12px; font-size:0.85rem;" onclick="viewEvidence('${f.company_id}')">
          View Regulatory Evidence (${c.evidence_count || 0})
        </button>
        ${f.source_url ? `<a href="${f.source_url}" target="_blank" class="btn btn-glass" style="padding:6px 12px; font-size:0.85rem;">Official Registry Record</a>` : ""}
      </div>
    `;
    box.appendChild(div);
  });

  // 4. Update Results Map
  if (resultsMap) {
    resultsMarkers.forEach((m) => resultsMap.removeLayer(m));
    resultsMarkers = [];

    const lat = data.incident.latitude;
    const lon = data.incident.longitude;
    resultsMap.setView([lat, lon], 13);

    // Incident marker
    const incM = L.circleMarker([lat, lon], {
      radius: 10,
      color: "#ff3333",
      fillColor: "#ff0000",
      fillOpacity: 0.9,
      weight: 3,
    })
      .addTo(resultsMap)
      .bindPopup(`<b>Waste Incident</b><br>${data.incident.waste_type}<br>${data.incident.quantity_tonnes} tonnes`);
    resultsMarkers.push(incM);

    // Candidate markers
    data.candidates.forEach((c) => {
      const f = c.facility;
      const color = c.score >= 70 ? "#ff6b35" : c.score >= 40 ? "#f7c548" : "#2ec4b6";
      const cm = L.circleMarker([f.latitude, f.longitude], {
        radius: 8,
        color: color,
        fillColor: color,
        fillOpacity: 0.8,
        weight: 2,
      })
        .addTo(resultsMap)
        .bindPopup(`<b>${f.company_name}</b><br>Score: ${c.score.toFixed(1)}/100<br>Distance: ${c.distance_km.toFixed(2)} km`);
      resultsMarkers.push(cm);
    });
  }

  showScreen("results");
}

// ── Application Initialization ──────────────────────
async function init() {
  try {
    // 1. Fetch Health Stats
    const health = await getJSON("/api/health").catch(() => null);
    if (health && $("heroStats")) {
      $("heroStats").innerHTML = `
        <div class="stat-item"><span class="stat-num">${health.facilities}</span><span class="stat-label">Monitored Facilities</span></div>
        <div class="stat-item"><span class="stat-num">${health.incidents}</span><span class="stat-label">Known Incidents</span></div>
        <div class="stat-item"><span class="stat-num">${health.evidence_companies}</span><span class="stat-label">Regulated Companies</span></div>
      `;
    }

    // 2. Fetch Data
    incidents = await getJSON("/api/incidents");
    facilities = await getJSON("/api/facilities");

    // Populate dropdown
    const select = $("incidentSelect");
    if (select) {
      select.innerHTML = incidents
        .map(
          (i) =>
            `<option value="${i.incident_id}">${i.incident_id} — ${i.waste_type} (${i.is_synthetic ? "seeded demo" : "observed"})</option>`
        )
        .join("");

      select.addEventListener("change", (e) => selectIncident(e.target.value));
    }

    // 3. Initialize Home Map
    const homeEl = $("homeMap");
    if (homeEl) {
      homeMap = L.map("homeMap").setView([17.533, 78.181], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors",
      }).addTo(homeMap);

      facilities.forEach((f) => {
        const m = L.circleMarker([f.latitude, f.longitude], {
          radius: 7,
          color: "#3b82f6",
          fillColor: "#60a5fa",
          fillOpacity: 0.8,
        })
          .addTo(homeMap)
          .bindPopup(`<b>${f.company_name}</b><br>${f.industry}`);
        homeMarkers.push(m);
      });
    }

    // 4. Initialize Incident Input Map
    const incEl = $("incidentMap");
    if (incEl) {
      incidentMap = L.map("incidentMap").setView([17.533, 78.181], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors",
      }).addTo(incidentMap);

      facilities.forEach((f) => {
        L.circleMarker([f.latitude, f.longitude], {
          radius: 6,
          color: "#3b82f6",
          fillColor: "#93c5fd",
          fillOpacity: 0.6,
        })
          .addTo(incidentMap)
          .bindPopup(`<b>${f.company_name}</b>`);
      });
    }

    // 5. Initialize Results Map
    const resEl = $("resultsMap");
    if (resEl) {
      resultsMap = L.map("resultsMap").setView([17.533, 78.181], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors",
      }).addTo(resultsMap);
    }

    // Default select first incident
    if (incidents.length > 0) {
      selectIncident(incidents[0].incident_id);
    }

    // Input change listeners
    ["lat", "lon"].forEach((id) => {
      const el = $(id);
      if (el) el.addEventListener("input", updateIncidentMap);
    });

    // Investigate button listener
    const invBtn = $("investigate");
    if (invBtn) {
      invBtn.addEventListener("click", async () => {
        const overlay = $("loadingOverlay");
        if (overlay) overlay.classList.add("active");
        setStatus("Running attribution analysis...");

        try {
          const payload = {
            incident_id: $("incidentSelect") ? $("incidentSelect").value : "CUSTOM_INCIDENT",
            latitude: Number($("lat").value),
            longitude: Number($("lon").value),
            date: $("date").value || new Date().toISOString().split("T")[0],
            waste_type: $("wasteType").value,
            quantity_tonnes: Number($("qty").value) || 1.0,
            is_synthetic: true,
            description: $("description") ? $("description").value : "User reported incident",
          };

          await getJSON("/api/incidents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          const data = await getJSON(
            `/api/incidents/${encodeURIComponent(payload.incident_id)}/investigate`,
            { method: "POST" }
          );

          renderResults(data);
          setStatus("Investigation complete.");
        } catch (err) {
          console.error(err);
          setStatus("Investigation failed. Check console or server logs.");
        } finally {
          if (overlay) overlay.classList.remove("active");
        }
      });
    }
  } catch (err) {
    console.error("Initialization error:", err);
    setStatus("Could not load application data.");
  }
}

// Launch application on window load
window.addEventListener("DOMContentLoaded", init);

