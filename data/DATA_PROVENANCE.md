# WasteTrace data provenance

## Real public facility records

The following company/facility records are based on public records. URLs are retained in `facilities.csv`.

1. **Arene Life Sciences Pvt. Ltd.**
   - Environmental Clearance record for Plot Nos. 48,49,50,209,210,211, Phase-II IDA Pashamylaram.
   - Public environmental-clearance record reports bounded latitude 17°31'57.95" N for this project and the project area at Pashamylaram.
   - Arene's own website confirms Unit 1 at the same Phase-II address and describes API manufacturing.

2. **Suven Pharmaceuticals Ltd. / Suven Life Sciences Ltd.**
   - Public environmental-clearance record for Plot Nos. 262-266, 269-271, 274 and 279, Phase-II IDA Pashamylaram.
   - Public Telangana iPASS record lists the company at those plots as Pharmaceuticals.

3. **Sanozen Pharma Pvt. Ltd.**
   - Public environmental-clearance record for Plot Nos. 170,171,172, Phase-II IDA Pashamylaram.
   - The record lists API / synthetic-organic-chemical activity and product information.

4. **Valentis Laboratories Pvt. Ltd.**
   - Public OCMMS/iPASS and company records place the company at Plot Nos. 29-32,39-42, Phase-II IDA Pashamylaram and identify pharmaceutical / chemical activities.

5. **Chromo Laboratories India Pvt. Ltd.**
   - Telangana iPASS record lists Plot Nos. 43 & 44, Phase-II Pashamylaram and the activity as basic chemicals/electrochemicals including acid manufacture.

6. **ITW India Pvt. Ltd. (Chemin)**
   - Telangana OCMMS and iPASS records list Plot Nos. 34-37, Phase-II Pashamylaram and organic-chemical manufacturing. OCMMS also exposes hazardous-waste authorization information.

7. **Gland Pharma Ltd.**
   - Telangana iPASS record lists plots 11,84-89, TSIIC Pashamylaram and pharmaceutical activity.

8. **MSN Laboratories Pvt. Ltd. – Biotech Division**
   - Telangana iPASS record lists the Pashamylaram facility and pharmaceutical activity.

## Synthetic incidents

`incidents.csv` contains synthetic incidents. Their coordinates are selected near the real facility cluster so the scoring pipeline can be demonstrated. They are NOT claims that those companies created or dumped waste there.

Each synthetic record has `is_synthetic=true` and an explanatory note.

## Historical benchmark

`historical_cases.csv` includes a public legal record:

- *Mystery Gas Spreads Panic v. Director, A.P. Pollution Control Board* (Andhra Pradesh High Court, 11 July 2001).
- The judgment states that a tanker originating from M/s Global Drugs Ltd. was intercepted and that the inquiry observed illegal dumping of highly concentrated acidic effluents; it also mentions a closure order dated 23 March 2000.
- Source: https://indiankanoon.org/doc/1066974/

This is a historical benchmark/context record. It is not treated as a current allegation.
