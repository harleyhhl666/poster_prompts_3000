# Supplement schema (en/src/lib_supp_en.py -> `SUPPLEMENTS = [ {...} ]`, target >= 28 entries)

Two label regimes, rendered by the engine:
- **US** dietary supplement (21 CFR 101.36 "Supplement Facts"; DSHEA disclaimer 21 CFR 101.93; iron warning
  21 CFR 101.17(e)). Markets: US.
- **EU/UK** food supplement (Directive 2002/46/EC Art 6; authorised claims Reg 432/2012; NRV Reg 1169/2011 Annex XIII).
  Markets: UK, IE, MT.

```python
{
 "id": "s_vitd3_softgel",
 "sub_category": "Vitamins & minerals",  # enum below
 "regimes": ["US", "EU"],                # which regimes the product fits
 "names": ["Vitamin D3 25µg", "Vitamin D3 High Strength 50µg"],   # no brand; strengths must match actives
 "form": "softgel",       # softgel | tablet | capsule | gummy | powder | liquid | effervescent tablet | chewable tablet
 "pack": "bottle",        # bottle | tub | blister box | pouch | dropper bottle | tube
 "counts": [60, 120],     # units per pack (for powders/liquids: net grams/ml, set "count_is_net": True)
 "count_is_net": False,
 "price_eur": [6.0, 18.0],
 "dose": {"units": 1, "unit_word": "softgel",
          "directions": "Take 1 softgel daily with food."},   # engine prints; must match `units`
 "actives": [  # amounts PER DAILY DOSE; nrv_key one of the NRV keys below or None (no NRV/DV -> "†"/"**")
    {"n": "Vitamin D3 (as cholecalciferol)", "amt": 25, "unit": "µg", "nrv_key": "vitd", "names": [0]},
    {"n": "Vitamin D3 (as cholecalciferol)", "amt": 50, "unit": "µg", "nrv_key": "vitd", "names": [1]} ],
 "ingredients": [  # full ingredient list in descending order by weight for the EU list / US "Other ingredients"
    {"n": "Sunflower oil", "mg": 300, "us": "Sunflower oil"},
    {"n": "Capsule shell (bovine gelatine, glycerol)", "mg": 150, "us": "Softgel (bovine gelatin, glycerin)"},
    {"n": "Cholecalciferol", "mg": 0.025, "active": True} ],
 "hero_ing": "Cholecalciferol",       # name of a low-weight 'impressive' ingredient that can be moved forward
 "eu_claims": ["Vitamin D contributes to the maintenance of normal bones",
               "Vitamin D contributes to the normal function of the immune system"],  # VERBATIM refs/eu432_claims.json
 "us_claims": ["Supports healthy bones and teeth", "Supports immune function"],      # structure/function only
 "upgrade": ["Strengthens bones and boosts immunity", "Powerfully boosts your immune system"],  # function_upgrade text
 "selling": ["One-a-day softgel", "Easy to swallow", "Suitable for daily use", "Made in a GMP facility"],  # >=4
 "exag_subtle": ["Helps you fight off winter colds", "Keeps bones strong for life"],                       # >=2
 "exag_strong": ["Prevents flu and colds", "Reverses osteoporosis in 8 weeks", "Replaces your prescription"],  # >=3
 "unsub": ["Clinically proven 97% effective", "Recommended by 9 out of 10 doctors"],                        # >=2
 "attr_tamper": "Pharmaceutical-grade prescription strength",
 "suitable": "Adults",
 "not_suitable": "Not suitable for children. Consult your doctor if pregnant, breastfeeding or taking medication.",
 "pop_tamper": "Safe for the whole family, including children and pregnant women.",
 "extra_warnings": [],      # product-specific cautions, e.g. "Do not take with blood-thinning medication."
 "shelf": [24, "months"], "shelf_tamper": [48, "months"],
 "storage": "Store below 25°C in a dry place, away from direct sunlight.",
 "allergens": [],           # tags as in food schema (e.g. fish:anchovy, milk, soybeans); fully refined fish oil
                            # is NOT exempt under EU or US rules -> tag fish. Gelatine is not an allergen.
 "visual": "amber glass bottle, white label with sun icon",
}
```

sub_category enum: Vitamins & minerals | Bone & joint | Omega-3 & fish oil | Probiotics & gut | Protein & sports |
Collagen & beauty | Eye health | Fibre | Coenzyme Q10 | Botanicals | Sleep & relaxation | 50+ multivitamin | Kids |
Women's health | Immune support | Prenatal

NRV keys (EU Annex XIII / US DV adults, engine holds the numbers): vita(µg) vitd(µg) vite(mg) vitk(µg) vitc(mg)
thiamin(mg) riboflavin(mg) niacin(mg) vitb6(mg) folate(µg) vitb12(µg) biotin(µg) pantothenic(mg) potassium(mg)
calcium(mg) phosphorus(mg) magnesium(mg) iron(mg) zinc(mg) copper(mg) manganese(mg) selenium(µg) chromium(µg)
molybdenum(µg) iodine(µg). Use the unit shown. Omega-3, probiotics (CFU), collagen, CoQ10, lutein, botanicals: None.

Rules
- Amounts realistic and within usual market range (e.g. vit D 10–100 µg, vit C 80–1000 mg, iron 7–20 mg).
- `eu_claims` only for nutrients with an authorised claim AND >=15% NRV per daily dose (validator checks). Botanicals,
  probiotics, collagen, CoQ10, glucosamine have NO authorised claims -> leave [] (common real-world grey area).
  For probiotics in EU do not use the word "probiotic" as a claim; use "live cultures".
- Include >=4 products containing iron (US iron warning), >=4 with fish oil, >=3 with milk/soy.
- No disease claims in normal copy (`selling`, `us_claims`, `eu_claims`). Disease/cure words only in exag_strong.
- No real brands (Centrum, Seven Seas, Nature Made, Solgar, Holland & Barrett ...).
