# AI-coder handoff prompt

You are extending an existing project called WasteTrace. Read the repository before changing anything.

The product is an AI-assisted industrial waste source-attribution prototype for Pashamylaram/Patancheru, Telangana.

DO NOT turn this into a generic sustainability dashboard.
DO NOT add blockchain, IoT, multi-agent systems, mobile apps, stock prediction, or microservices.

The core flow must remain:

incident -> nearby real facilities -> interpretable attribution score -> evidence -> investigation report

Use the existing seeded data and preserve its provenance labels.
Synthetic incidents are synthetic and must never be presented as real pollution allegations.
Real company records come from public environmental/regulatory sources listed in DATA_PROVENANCE.md.

The system must never state that a company is legally guilty. Use language such as:
- potential source
- investigation candidate
- evidence is consistent with
- requires field/regulatory verification

When improving the project:
1. Keep the current app runnable with `python run.py`.
2. Keep tests passing.
3. Keep the scoring weights explicit and explainable.
4. Add source links for factual company information.
5. Treat missing data neutrally.
6. Do not invent regulatory violations, production values, or coordinates.

Before making architectural changes, explain why they are necessary and keep the implementation simple enough for a student hackathon demo.
