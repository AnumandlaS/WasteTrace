import math
import re
from datetime import date
from typing import Dict, List, Tuple
from .config import SCORING_WEIGHTS
from .models import Incident, Facility

WASTE_ALIASES = {
    "spent_solvent_containers": {"solvent", "container", "organic", "pharma", "chemical"},
    "acidic_chemical_residue": {"acid", "chemical", "corrosive", "residue", "sludge"},
    "pharmaceutical_sludge": {"pharma", "pharmaceutical", "sludge", "chemical", "organic", "residue"},
    "organic_chemical_residue": {"organic", "chemical", "residue", "solvent"},
    "plastic_packaging": {"plastic", "packaging", "polymer"},
    "metal_scrap": {"metal", "scrap", "slag", "steel"},
}

INDUSTRY_TERMS = {
    "pharmaceutical": {"pharma", "pharmaceutical", "api", "solvent", "chemical", "sludge", "intermediate", "organic"},
    "chemical": {"chemical", "acid", "organic", "solvent", "residue"},
    "basic chemicals": {"chemical", "acid", "residue", "corrosive"},
    "organic chemicals": {"organic", "chemical", "solvent", "residue"},
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def spatial_score(distance_km: float, radius_km: float = 10.0) -> float:
    # Smooth decay to zero at the configured radius.
    if distance_km >= radius_km:
        return 0.0
    return max(0.0, 1.0 - (distance_km / radius_km) ** 1.6)


def tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def waste_score(incident_type: str, facility: Facility) -> Tuple[float, str]:
    target = WASTE_ALIASES.get(incident_type, tokens(incident_type.replace("_", " ")))
    profile = tokens(" ".join([facility.industry, facility.products, facility.waste_types]))
    overlap = target & profile
    # Reward both breadth and a few high-value semantic keywords.
    if not target:
        return 0.0, "No waste vocabulary available."
    score = min(1.0, len(overlap) / max(2, min(5, len(target))))
    if "acid" in target and ("acid" in profile or "chemical" in profile):
        score = max(score, 0.85)
    if "pharma" in target and "pharmaceutical" in profile:
        score = max(score, 0.90)
    if "solvent" in target and "solvent" in profile:
        score = max(score, 0.92)
    matched = ", ".join(sorted(overlap)) if overlap else "no strong keyword overlap"
    return score, matched


def capacity_score(quantity_tonnes: float, facility: Facility) -> float:
    # Capacity is optional in this MVP. Missing capacity is neutral (0.5), never suspicious.
    if facility.production_capacity_tpa is None or facility.production_capacity_tpa <= 0:
        return 0.5
    annual_waste_scale = max(1.0, quantity_tonnes * 365)
    ratio = annual_waste_scale / facility.production_capacity_tpa
    # A generated incident is plausible across a wide range; this is deliberately low-weight.
    if ratio <= 0.25:
        return 1.0
    if ratio <= 0.75:
        return 0.85
    if ratio <= 1.5:
        return 0.65
    if ratio <= 3.0:
        return 0.45
    return 0.25


def temporal_score(incident_date: str, facility: Facility) -> float:
    # Real public records in the seed dataset do not encode complete validity intervals.
    # We therefore keep this neutral rather than fabricating operating-status dates.
    return 0.5


def regulatory_score(facility: Facility) -> float:
    status = facility.regulatory_status.lower()
    if "public" in status or "authorization" in status or "environmental" in status:
        return 1.0
    return 0.5


def score_candidate(incident: Incident, facility: Facility) -> Dict:
    distance = haversine_km(incident.latitude, incident.longitude, facility.latitude, facility.longitude)
    s_spatial = spatial_score(distance)
    s_waste, match_note = waste_score(incident.waste_type, facility)
    s_capacity = capacity_score(incident.quantity_tonnes, facility)
    s_temporal = temporal_score(incident.date, facility)
    s_regulatory = regulatory_score(facility)
    total = (
        SCORING_WEIGHTS["spatial"] * s_spatial
        + SCORING_WEIGHTS["waste"] * s_waste
        + SCORING_WEIGHTS["capacity"] * s_capacity
        + SCORING_WEIGHTS["temporal"] * s_temporal
        + SCORING_WEIGHTS["regulatory"] * s_regulatory
    )
    return {
        "company_id": facility.company_id,
        "company_name": facility.company_name,
        "distance_km": round(distance, 3),
        "score": round(total * 100, 2),
        "components": {
            "spatial": round(s_spatial * 100, 2),
            "waste": round(s_waste * 100, 2),
            "capacity": round(s_capacity * 100, 2),
            "temporal": round(s_temporal * 100, 2),
            "regulatory": round(s_regulatory * 100, 2),
        },
        "waste_match": match_note,
    }


def rank_candidates(incident: Incident, facilities: List[Facility], max_radius_km=10.0):
    ranked = []
    for facility in facilities:
        result = score_candidate(incident, facility)
        if result["distance_km"] <= max_radius_km:
            ranked.append(result)
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
