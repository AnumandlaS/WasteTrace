# WasteTrace MVP system design

## Goal

For a waste incident at `(lat, lon, date, waste_type, quantity)`, rank nearby industrial facilities by how consistent they are with being a possible source.

## Inputs

- Incident coordinates
- Incident date
- Waste category
- Estimated quantity
- Optional image (reserved for future detector)

## Candidate retrieval

Find all seeded industrial facilities inside a 10 km radius using Haversine distance.

## Scoring

`score = .35 spatial + .30 waste + .20 capacity + .10 temporal + .05 regulatory`

All component values are 0–100.

### Spatial

A smooth distance-decay function. Score becomes zero at 10 km.

### Waste compatibility

Keyword/taxonomy matching between the incident class and company industry/products/known waste types. This is intentionally interpretable and can later be swapped for an embedding model.

### Capacity

Uses production-capacity information when available. If missing, returns 50 rather than treating the missing value as suspicious.

### Temporal

Neutral in v1 because the public seed does not contain complete historical validity intervals for every consent. This is a placeholder for a later verified operating-period adapter.

### Regulatory evidence

Rewards the presence of public regulatory/environmental records. This is an evidence-availability signal, not an accusation signal.

## Evidence layer

Every company row stores a source URL and source note. The optional Gemini layer summarizes only the structured facts supplied by the server.

## Ground truth / evaluation

Synthetic demo incidents have a `ground_truth_company` used for local experimentation. This field is never sent to the LLM and is not shown in the UI as proof.

For a research evaluation, report Top-1 and Top-3 candidate recall over held-out incidents. Do not report legal attribution accuracy unless you have independently verified field/chain-of-custody ground truth.

## Next research upgrade

1. Replace synthetic incidents with georeferenced observations from a published dumpsite dataset.
2. Add Sentinel-2 / Planet imagery and an existing detector.
3. Add environmental-document RAG.
4. Add chemical fingerprint inputs from field/lab samples.
5. Train a probabilistic source-attribution model using verified labeled samples.
