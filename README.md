# WasteTrace

AI-assisted industrial waste source attribution and investigation prioritization.

## What this prototype does

WasteTrace takes a suspected industrial-waste incident and:

1. finds nearby industrial facilities;
2. compares the incident waste type with each facility's industry/waste profile;
3. combines spatial, waste, capacity, temporal and regulatory signals into an interpretable attribution score;
4. ranks potential source companies;
5. shows the evidence supporting each candidate; and
6. generates an investigation report.

**Important:** WasteTrace does **not** determine legal guilt. It produces an investigation-priority ranking that requires field/regulatory verification.

## Case study

The seeded case study is **Pashamylaram / Patancheru, Sangareddy, Telangana, India**.

The company/facility records are based on public Telangana/environmental-clearance/regulatory material. Some coordinates are represented as **plot-area centroids / approximate points** derived from publicly reported coordinate bounds, not surveyed facility gates.

The demo incidents are **synthetic incidents** designed to exercise the ranking pipeline against the real facility dataset. This is deliberate: public data gives us real corporate/facility context without fabricating a real accusation against a currently operating company.

A separate historical benchmark record is included for the 2001 Andhra Pradesh High Court matter describing a tanker originating from Global Drugs Ltd. and illegal dumping of concentrated acidic effluent. That historical case is used as research/evaluation context, not as a model-generated accusation.

## Quick start (Windows PowerShell)

```powershell
cd wastetrace
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Then open:

http://127.0.0.1:8000

## Optional Gemini evidence narrative

The app works without an API key. If `GEMINI_API_KEY` is present, it can use Gemini to turn the structured evidence into a concise narrative. The LLM is **not** allowed to invent facts; the prompt supplies the retrieved evidence and the UI still displays the source URLs.

PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
python run.py
```

## Data provenance

See `data/DATA_PROVENANCE.md` for the source-by-source provenance and what is real vs synthetic.

## Architecture

```text
Synthetic / observed incident
          |
          v
   FastAPI incident API
          |
          v
 Candidate facility retrieval
          |
          v
 Interpretable attribution scorer
  |       |       |       |       |
space   waste   capacity  time  evidence
          |
          v
  Ranked investigation candidates
          |
          v
 Evidence panel + optional Gemini narrative
          |
          v
     Investigation report
```

## Research references

- GISLab-ELTE/WasteDetection: https://github.com/GISLab-ELTE/WasteDetection
- Magyar et al., "Waste Detection and Change Analysis based on Multispectral Satellite Imagery" (2023): https://arxiv.org/abs/2303.14521
- Nature Communications dumpsite detection paper (2023): https://www.nature.com/articles/s41467-023-37136-1
- Mu et al., "High-precision identification of industrial inorganic wastes via dual-layer machine learning" (2026): https://doi.org/10.1016/j.jece.2026.122719
- Industrial waste fingerprinting / source identification (2026): https://doi.org/10.1016/j.jhazmat.2026.141699
- OECD, Digital technologies for better enforcement of waste regulation and elimination of waste crime (2024): https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/04/digital-technologies-for-better-enforcement-of-waste-regulation-and-elimination-of-waste-crime_5976ab1a/6739f625-en.pdf

## Limitations

- The demo does not train a satellite waste detector. It starts from a detected incident.
- The facility coordinates are approximate for some records.
- Capacity and waste-profile data is incomplete for many real facilities; missing fields are treated neutrally rather than as suspicious.
- The attribution score is a prototype scoring framework, not a validated legal or forensic standard.
