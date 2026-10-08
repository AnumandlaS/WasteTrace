from pathlib import Path
from datetime import datetime
from html import escape
from .config import REPORT_DIR


def build_finding(incident, candidate, facility):
    level = (
        "HIGH PRIORITY" if candidate["score"] >= 75
        else "MEDIUM PRIORITY" if candidate["score"] >= 55
        else "LOW PRIORITY"
    )
    return {
        "level": level,
        "summary": (
            f"{facility.company_name} is a {level.lower()} investigation candidate "
            f"with an attribution score of {candidate['score']:.1f}/100."
        ),
        "reasons": [
            f"Facility distance: {candidate['distance_km']:.2f} km.",
            f"Waste compatibility: {candidate['components']['waste']:.1f}/100 ({candidate['waste_match']}).",
            f"Spatial proximity: {candidate['components']['spatial']:.1f}/100.",
            f"Capacity plausibility: {candidate['components']['capacity']:.1f}/100.",
            f"Regulatory evidence availability: {candidate['components']['regulatory']:.1f}/100.",
        ],
    }


def _score_color(score):
    if score >= 75:
        return "#ef4444"
    elif score >= 55:
        return "#f59e0b"
    else:
        return "#22c55e"


def _level_badge(level):
    colors = {
        "HIGH PRIORITY": ("#fef2f2", "#ef4444"),
        "MEDIUM PRIORITY": ("#fffbeb", "#f59e0b"),
        "LOW PRIORITY": ("#f0fdf4", "#22c55e"),
    }
    bg, fg = colors.get(level, ("#f3f4f6", "#6b7280"))
    return f"<span style='background:{bg};color:{fg};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700'>{level}</span>"


def generate_html_report(incident, ranked, facilities, evidence=None, waste_profiles=None):
    top = ranked[:5]
    facility_map = {f.company_id: f for f in facilities}
    evidence = evidence or {}
    waste_profiles = waste_profiles or {}

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    incident_flag = "SYNTHETIC DEMO INCIDENT" if incident.is_synthetic else "OBSERVED INCIDENT"
    flag_color = "#818cf8" if incident.is_synthetic else "#ef4444"

    # Build candidate rows
    candidate_rows = ""
    for idx, item in enumerate(top):
        f = facility_map[item["company_id"]]
        finding = build_finding(incident, item, f)
        score_col = _score_color(item["score"])

        # Evidence entries for this company
        ev_list = evidence.get(item["company_id"], [])
        ev_html = ""
        for ev in ev_list:
            ev_html += f"""
            <div style="padding:8px 12px;background:#f8fafc;border-radius:8px;margin:4px 0;border-left:3px solid #94a3b8">
                <div style="font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:0.5px">{escape(ev.evidence_type.replace('_',' '))}</div>
                <div style="font-size:13px;color:#334155;margin-top:2px">{escape(ev.description)}</div>
                <a href="{escape(ev.source_url)}" style="font-size:12px;color:#3b82f6;text-decoration:none">{escape(ev.document_name)}</a>
            </div>
            """

        # Waste profiles for this company
        wp_list = waste_profiles.get(item["company_id"], [])
        wp_html = ""
        for wp in wp_list:
            qty = f" — {wp.authorized_quantity:.0f} TPA authorized" if wp.authorized_quantity else ""
            wp_html += f"<li style='margin:2px 0;font-size:13px;color:#475569'>{escape(wp.waste_type.replace('_',' ').title())}: {escape(wp.waste_description)}{qty}</li>"

        candidate_rows += f"""
        <div style="border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin:16px 0;page-break-inside:avoid">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <div>
                    <div style="font-size:12px;color:#94a3b8;margin-bottom:4px">#{idx+1} Investigation Candidate</div>
                    <h3 style="margin:0;color:#0f172a;font-size:18px">{escape(f.company_name)}</h3>
                    <div style="font-size:13px;color:#64748b;margin-top:2px">{escape(f.industry)} · {escape(f.address)}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:32px;font-weight:800;color:{score_col}">{item['score']:.1f}</div>
                    <div style="font-size:11px;color:#94a3b8">/ 100</div>
                </div>
            </div>
            {_level_badge(finding['level'])}
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0">
                <div style="background:#f1f5f9;padding:12px;border-radius:8px">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase">Distance</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a">{item['distance_km']:.2f} km</div>
                </div>
                <div style="background:#f1f5f9;padding:12px;border-radius:8px">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase">Spatial Score</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a">{item['components']['spatial']:.1f}%</div>
                </div>
                <div style="background:#f1f5f9;padding:12px;border-radius:8px">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase">Waste Match</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a">{item['components']['waste']:.1f}%</div>
                </div>
                <div style="background:#f1f5f9;padding:12px;border-radius:8px">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase">Capacity</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a">{item['components']['capacity']:.1f}%</div>
                </div>
            </div>
            <div style="margin-top:12px">
                <div style="font-size:13px;font-weight:600;color:#334155;margin-bottom:4px">Waste Match Keywords</div>
                <div style="font-size:13px;color:#64748b">{escape(item['waste_match'])}</div>
            </div>
            {'<div style="margin-top:16px"><div style="font-size:13px;font-weight:600;color:#334155;margin-bottom:8px">Waste Profile</div><ul style="margin:0;padding-left:20px">' + wp_html + '</ul></div>' if wp_html else ''}
            {'<div style="margin-top:16px"><div style="font-size:13px;font-weight:600;color:#334155;margin-bottom:8px">Source Evidence</div>' + ev_html + '</div>' if ev_html else ''}
            <div style="margin-top:12px">
                <a href="{escape(f.source_url)}" style="font-size:13px;color:#3b82f6;text-decoration:none">Open primary source record →</a>
            </div>
        </div>
        """

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>WasteTrace Investigation Report — {escape(incident.incident_id)}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0 }}
    body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 24px; color: #0f172a; line-height: 1.6; background: #fff }}
    @media print {{ body {{ padding: 20px }} }}
    a {{ color: #3b82f6; text-decoration: none }}
    a:hover {{ text-decoration: underline }}
</style>
</head>
<body>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:32px;padding-bottom:20px;border-bottom:2px solid #e2e8f0">
        <div>
            <h1 style="font-size:28px;font-weight:800;color:#0f172a;margin-bottom:4px">WasteTrace Investigation Report</h1>
            <div style="font-size:13px;color:#94a3b8">Generated {timestamp}</div>
        </div>
        <span style="background:{flag_color}15;color:{flag_color};padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600">{incident_flag}</span>
    </div>

    <div style="background:#f8fafc;padding:20px;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:24px">
        <h2 style="font-size:16px;color:#64748b;margin-bottom:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600">Incident Details</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
            <div>
                <div style="font-size:12px;color:#94a3b8">ID</div>
                <div style="font-weight:600">{escape(incident.incident_id)}</div>
            </div>
            <div>
                <div style="font-size:12px;color:#94a3b8">Location</div>
                <div style="font-weight:600">{incident.latitude:.6f}, {incident.longitude:.6f}</div>
            </div>
            <div>
                <div style="font-size:12px;color:#94a3b8">Date</div>
                <div style="font-weight:600">{escape(incident.date)}</div>
            </div>
            <div>
                <div style="font-size:12px;color:#94a3b8">Waste Type</div>
                <div style="font-weight:600">{escape(incident.waste_type.replace('_', ' ').title())}</div>
            </div>
            <div>
                <div style="font-size:12px;color:#94a3b8">Estimated Quantity</div>
                <div style="font-weight:600">{incident.quantity_tonnes:.2f} tonnes</div>
            </div>
        </div>
    </div>

    <h2 style="font-size:20px;font-weight:700;margin:28px 0 16px">Ranked Investigation Candidates</h2>
    {candidate_rows}

    <div style="background:#fffbeb;border:1px solid #fde68a;padding:20px;border-radius:12px;margin:32px 0">
        <h3 style="color:#92400e;font-size:14px;margin-bottom:8px">⚠️ Important Limitation</h3>
        <p style="color:#78350f;font-size:13px;line-height:1.7;margin:0">
            This report is an AI-assisted investigation aid. Attribution scores are not legal
            determinations of responsibility. Facility coordinates may be approximate; missing
            data is treated neutrally rather than as indicative of wrongdoing. Field sampling,
            chain-of-custody evidence, regulatory records, and independent investigation are
            required before attributing legal responsibility to any entity.
        </p>
    </div>

    <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px;border-top:1px solid #e2e8f0;margin-top:32px">
        WasteTrace · AI-Assisted Industrial Waste Source Attribution · {timestamp}
    </div>
</body>
</html>"""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{incident.incident_id}_report.html"
    path.write_text(html, encoding="utf-8")
    return path
