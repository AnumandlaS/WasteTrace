import csv
from pathlib import Path
from typing import Dict, List
from .config import DATA_DIR
from .models import Incident, Facility, WasteProfile, Evidence, HistoricalCase


def _read_csv(name: str):
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_incidents() -> Dict[str, Incident]:
    out = {}
    for row in _read_csv("incidents.csv"):
        out[row["incident_id"]] = Incident(
            incident_id=row["incident_id"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            date=row["date"],
            waste_type=row["waste_type"],
            quantity_tonnes=float(row["quantity_tonnes"]),
            is_synthetic=row["is_synthetic"].lower() == "true",
            ground_truth_company=row.get("ground_truth_company") or None,
            description=row.get("description", ""),
        )
    return out


def load_facilities() -> Dict[str, Facility]:
    out = {}
    for row in _read_csv("facilities.csv"):
        cap = row.get("production_capacity_tpa", "").strip()
        out[row["company_id"]] = Facility(
            company_id=row["company_id"],
            company_name=row["company_name"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            coord_type=row["coord_type"],
            industry=row["industry"],
            products=row["products"],
            waste_types=row["waste_types"],
            production_capacity_tpa=float(cap) if cap else None,
            regulatory_status=row["regulatory_status"],
            address=row["address"],
            source_url=row["source_url"],
            source_note=row["source_note"],
        )
    return out


def load_waste_profiles() -> Dict[str, List[WasteProfile]]:
    """Load waste profiles grouped by company_id."""
    out: Dict[str, List[WasteProfile]] = {}
    for row in _read_csv("waste_profiles.csv"):
        qty = row.get("authorized_quantity", "").strip()
        wp = WasteProfile(
            company_id=row["company_id"],
            waste_type=row["waste_type"],
            waste_description=row["waste_description"],
            authorized_quantity=float(qty) if qty else None,
            source_document=row["source_document"],
        )
        out.setdefault(wp.company_id, []).append(wp)
    return out


def load_evidence() -> Dict[str, List[Evidence]]:
    """Load evidence records grouped by company_id."""
    out: Dict[str, List[Evidence]] = {}
    for row in _read_csv("evidence.csv"):
        ev = Evidence(
            company_id=row["company_id"],
            evidence_type=row["evidence_type"],
            description=row["description"],
            source_url=row["source_url"],
            document_name=row["document_name"],
        )
        out.setdefault(ev.company_id, []).append(ev)
    return out


def load_historical_cases() -> List[HistoricalCase]:
    """Load documented historical environmental cases."""
    cases = []
    for row in _read_csv("historical_cases.csv"):
        cases.append(HistoricalCase(
            case_id=row["case_id"],
            case_name=row["case_name"],
            date=row["date"],
            known_source=row["known_source"],
            location_context=row["location_context"],
            incident_type=row["incident_type"],
            source_url=row["source_url"],
            notes=row["notes"],
        ))
    return cases


def load_all():
    return (
        load_incidents(),
        load_facilities(),
        load_waste_profiles(),
        load_evidence(),
        load_historical_cases(),
    )
