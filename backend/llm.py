from .config import GEMINI_API_KEY, GEMINI_MODEL


def generate_narrative(incident, ranked, facilities):
    """Optional Gemini narrative. Falls back to deterministic text when no API key is available."""
    top = ranked[:3]
    facility_map = {f.company_id: f for f in facilities}
    if not top:
        return "No nearby candidate facilities were found within the configured search radius."

    if not GEMINI_API_KEY:
        first = facility_map[top[0]["company_id"]]
        return (
            f"The highest-ranked investigation candidate is {first.company_name} with an attribution score of "
            f"{top[0]['score']:.1f}/100. The score is driven by proximity ({top[0]['distance_km']:.2f} km) and "
            f"compatibility between the reported waste type and the facility's public industrial/waste profile. "
            "This is an investigation-priority result, not a legal finding."
        )

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        evidence = []
        for item in top:
            f = facility_map[item["company_id"]]
            evidence.append({
                "company": f.company_name,
                "score": item["score"],
                "distance_km": item["distance_km"],
                "waste_match": item["waste_match"],
                "industry": f.industry,
                "products": f.products,
                "waste_types": f.waste_types,
                "source_url": f.source_url,
            })
        prompt = f"""
You are summarizing an environmental investigation aid. Do not accuse any company of illegal activity.
Use ONLY the structured facts provided below.

Incident:
- id: {incident.incident_id}
- date: {incident.date}
- waste type: {incident.waste_type}
- quantity: {incident.quantity_tonnes} tonnes
- location: {incident.latitude}, {incident.longitude}

Candidates:
{evidence}

Write 120-180 words explaining why the top candidate was ranked highest and what evidence should be verified next.
Use careful wording such as 'candidate', 'consistent with', and 'requires verification'.
Do not add any facts not present in the input.
"""
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as exc:
        return f"Gemini narrative unavailable ({type(exc).__name__}). The deterministic evidence summary remains available."
