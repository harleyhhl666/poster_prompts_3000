# Reviewer rubric (English part of a rich-text AIGC prompt dataset)

Context: each row is a final image-generation prompt (for GPT Image) for a food label, retail ad, supplement label,
event poster or public-service poster set in Europe (EU/EEA, UK, Switzerland) or North America (US, Canada). Every
string inside 「」 must be drawn verbatim. Groups are triplets: `clean` (must be fully self-consistent and realistic),
`subtle` (1–2 hidden anomalies), `strong` (2–3 obvious but realistic anomalies). `tamper_details` lists the INTENDED
anomalies — those are NOT defects. For tampered rows the clean prompt of the same group is given for comparison.
Brands/companies/organisers are fictional on purpose.

Reference values: EU %RI per portion uses energy 8400 kJ, fat 70 g, saturates 20 g, carbohydrate 260 g, sugars 90 g,
protein 50 g, salt 6 g; EU energy kJ = 17*carb + 17*protein + 37*fat + 8*fibre. US %DV: fat 78 g, sat 20 g,
cholesterol 300 mg, sodium 2300 mg, total carb 275 g, fiber 28 g, added sugars 50 g, vit D 20 mcg, calcium 1300 mg,
iron 18 mg, potassium 4700 mg. Dataset date convention: best-before/expiry = production date + shelf life − 1 day;
the lot code encodes the production date (L27037B = 2027 day 037; L 060227 B = 06.02.27; LOT 270206-07 = 2027-02-06;
L20270206B). EU labels emphasise allergens in CAPITALS inside the ingredient list; US labels use a CONTAINS line.
Rounding: EU values ≥10 g to 1 g, <10 g to 0.1 g; US per FDA rules — allow small rounding differences.

For EACH prompt judge:
- generatable: can an image model draw it without inventing content (all text given, layout clear)? true/false
- realistic: plausible product/ad/poster for that country and market (prices, currency, units, spelling, regulation
  style, season vs date, English-language context in non-Anglophone countries)? true/false
- tamper_ok: for clean rows — no UNINTENDED contradiction or error; for tampered rows — every listed anomaly is really
  present in the prompt text, naturally embedded (not highlighted), and there is no extra unintended anomaly. true/false
- defects: list of concrete problems, each quoting the offending text (short)
- severity: "none" | "minor" (cosmetic/odd but usable) | "major" (unintended contradiction, wrong fact, ungeneratable,
  unrealistic for the market, or an intended anomaly missing)

Output: append one JSON object per prompt (one line each) to your verdict file:
{"id": ..., "variant": ..., "generatable": bool, "realistic": bool, "tamper_ok": bool, "defects": [...], "severity": ...}
Append after every 5 prompts (do not wait until the end). Read the batch in chunks (e.g. 5 lines at a time) to keep
tool outputs small. Be strict but do not flag intended anomalies. Final answer: counts by severity + the 5 most
important defect patterns (<= 15 lines).
