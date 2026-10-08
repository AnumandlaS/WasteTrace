from backend.models import Incident, Facility
from backend.scoring import haversine_km, score_candidate, rank_candidates


def fixture_incident():
    return Incident("X", 17.5324, 78.1801, "2026-09-14", "spent_solvent_containers", 2.5, True, None, "synthetic")


def fixture_facility():
    return Facility("C001", "Arene", 17.532025, 78.1803, "approx", "Pharmaceutical API manufacturing", "APIs", "spent solvents; chemical residues", None, "Public environmental record", "", "https://example.com", "test")


def test_distance_is_small():
    d = haversine_km(17.5324, 78.1801, 17.532025, 78.1803)
    assert d < 0.1


def test_candidate_score_is_high_for_matching_facility():
    result = score_candidate(fixture_incident(), fixture_facility())
    assert result["score"] > 70
    assert result["components"]["waste"] >= 80


def test_ranking_orders_candidates():
    incident = fixture_incident()
    close = fixture_facility()
    far = Facility("C002", "Far", 17.54, 78.19, "approx", "Glass", "Glass", "glass", None, "Public", "", "https://example.com", "test")
    ranked = rank_candidates(incident, [far, close])
    assert ranked[0]["company_id"] == "C001"
