from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from .config import FRONTEND_DIR, REPORT_DIR
from .data_store import load_all
from .scoring import rank_candidates
from .reporting import generate_html_report
from .llm import generate_narrative

app = FastAPI(title="WasteTrace", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents, facilities, waste_profiles, evidence, historical_cases = load_all()
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")


class IncidentInput(BaseModel):
    incident_id: str
    latitude: float
    longitude: float
    date: str
    waste_type: str
    quantity_tonnes: float
    is_synthetic: bool = True
    description: str = ""


# ── Pages ──────────────────────────────────────────────

@app.get("/", response_class=FileResponse)
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


# ── Health ─────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "incidents": len(incidents),
        "facilities": len(facilities),
        "evidence_companies": len(evidence),
        "historical_cases": len(historical_cases),
    }


# ── Incidents ──────────────────────────────────────────

@app.get("/api/incidents")
def get_incidents():
    return [x.to_dict() for x in incidents.values()]


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    item = incidents.get(incident_id)
    if not item:
        raise HTTPException(404, "Incident not found")
    return item.to_dict()


@app.post("/api/incidents")
def create_incident(payload: IncidentInput):
    incident = payload.model_dump()
    incident["ground_truth_company"] = None
    from .models import Incident
    obj = Incident(**incident)
    incidents[obj.incident_id] = obj
    return obj.to_dict()


# ── Facilities ─────────────────────────────────────────

@app.get("/api/facilities")
def get_facilities():
    return [x.to_dict() for x in facilities.values()]


@app.get("/api/companies/{company_id}")
def get_company(company_id: str):
    item = facilities.get(company_id)
    if not item:
        raise HTTPException(404, "Company not found")
    facility_dict = item.to_dict()
    # Enrich with waste profiles
    facility_dict["waste_profiles"] = [
        wp.to_dict() for wp in waste_profiles.get(company_id, [])
    ]
    return facility_dict


# ── Evidence ───────────────────────────────────────────

@app.get("/api/companies/{company_id}/evidence")
def get_company_evidence(company_id: str):
    item = facilities.get(company_id)
    if not item:
        raise HTTPException(404, "Company not found")
    company_evidence = [ev.to_dict() for ev in evidence.get(company_id, [])]
    company_waste = [wp.to_dict() for wp in waste_profiles.get(company_id, [])]
    return {
        "company_id": company_id,
        "company_name": item.company_name,
        "evidence": company_evidence,
        "waste_profiles": company_waste,
    }


# ── Investigation ─────────────────────────────────────

@app.post("/api/incidents/{incident_id}/investigate")
def investigate(incident_id: str):
    incident = incidents.get(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    ranked = rank_candidates(incident, list(facilities.values()))
    facility_map = {f.company_id: f for f in facilities.values()}
    candidates = []
    for item in ranked:
        f = facility_map[item["company_id"]]
        row = dict(item)
        row["facility"] = f.to_dict()
        # Add evidence count and waste profile count for quick display
        row["evidence_count"] = len(evidence.get(item["company_id"], []))
        row["waste_profile_count"] = len(waste_profiles.get(item["company_id"], []))
        candidates.append(row)
    narrative = generate_narrative(incident, ranked, list(facilities.values()))
    report_path = generate_html_report(incident, ranked, list(facilities.values()), evidence, waste_profiles)
    return {
        "incident": incident.to_dict(),
        "candidates": candidates,
        "narrative": narrative,
        "report_url": f"/reports/{report_path.name}",
    }


# ── Candidates (standalone) ───────────────────────────

@app.get("/api/incidents/{incident_id}/candidates")
def get_candidates(incident_id: str):
    incident = incidents.get(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    ranked = rank_candidates(incident, list(facilities.values()))
    return ranked


# ── Report ─────────────────────────────────────────────

@app.get("/api/incidents/{incident_id}/report")
def get_report(incident_id: str):
    incident = incidents.get(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    ranked = rank_candidates(incident, list(facilities.values()))
    report_path = generate_html_report(incident, ranked, list(facilities.values()), evidence, waste_profiles)
    return FileResponse(report_path, media_type="text/html")


@app.get("/reports/{filename}")
def report(filename: str):
    path = REPORT_DIR / filename
    if not path.exists() or path.parent != REPORT_DIR:
        raise HTTPException(404, "Report not found")
    return FileResponse(path)


# ── Historical Cases ───────────────────────────────────

@app.get("/api/historical-cases")
def get_historical_cases():
    return [c.to_dict() for c in historical_cases]
