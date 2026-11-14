def A(n, amt, unit, key=None, names=None):
    d = {"n": n, "amt": amt, "unit": unit, "nrv_key": key}
    if names is not None: d["names"] = names
    return d
def I(n, mg, us=None, active=False):
    d = {"n": n, "mg": mg, "us": us or n}
    if active: d["active"] = True
    return d

ITEMS = [
{"id": "s_biotin_hair_nails", "sub_category": "Collagen & beauty", "regimes": ["US", "EU"],
 "names": ["Hair, Skin & Nails with Biotin 2500µg", "Hair, Skin & Nails Extra Strength Biotin 5000µg"],
 "form": "tablet", "pack": "bottle", "counts": [60, 120], "count_is_net": False, "price_eur": [6.0, 18.0],
 "dose": {"units": 1, "unit_word": "tablet", "directions": "Take 1 tablet daily with food."},
 "actives": [A("Biotin", 2500, "µg", "biotin", [0]), A("Biotin", 5000, "µg", "biotin", [1]),
             A("Zinc (as zinc citrate)", 10, "mg", "zinc"), A("Copper (as copper gluconate)", 1, "mg", "copper"),
             A("Selenium (as sodium selenite)", 55, "µg", "selenium"), A("Horsetail extract (7% silica)", 100, "mg", None)],
 "ingredients": [I("Bulking agent: microcrystalline cellulose", 300, "Microcrystalline cellulose"),
                 I("Horsetail extract (7% silica)", 100, "Horsetail (Equisetum arvense) stem extract", True),
                 I("Zinc citrate", 31, "Zinc citrate", True), I("Glazing agent: hydroxypropyl methylcellulose", 20, "Hypromellose"),
                 I("Copper gluconate", 7, "Copper gluconate", True), I("Anti-caking agent: magnesium stearate", 6, "Magnesium stearate"),
                 I("Biotin", 5.0, "Biotin", True), I("Sodium selenite", 0.12, "Sodium selenite", True)],
 "hero_ing": "Biotin",
 "eu_claims": ["Biotin contributes to the maintenance of normal hair", "Biotin contributes to the maintenance of normal skin",
               "Zinc contributes to the maintenance of normal nails", "Selenium contributes to the maintenance of normal hair",
               "Copper contributes to normal hair pigmentation"],
 "us_claims": ["Supports healthy hair, skin and nails", "Supports keratin production", "Helps maintain natural hair colour"],
 "upgrade": ["Grows thicker hair in weeks", "Unbreakable nails guaranteed"],
 "selling": ["High-strength biotin", "With zinc, selenium and copper", "Plant-sourced silica from horsetail", "Vegan friendly"],
 "exag_subtle": ["Visibly thicker hair in 30 days", "Say goodbye to brittle nails"],
 "exag_strong": ["Cures hair loss and baldness", "Reverses alopecia", "Treats acne and eczema"],
 "unsub": ["92% saw longer hair in 4 weeks", "The secret of supermodels"],
 "attr_tamper": "Dermatologist-prescribed formula",
 "suitable": "Adults",
 "not_suitable": "Not suitable for children or during pregnancy. Consult your doctor if taking medication.",
 "pop_tamper": "Safe for children and teenagers at double the dose.",
 "extra_warnings": ["Biotin can interfere with some laboratory tests (e.g. thyroid and troponin); tell your doctor you take it."],
 "shelf": [24, "months"], "shelf_tamper": [48, "months"],
 "storage": "Store below 25°C in a dry place.", "allergens": [],
 "visual": "rose-gold bottle, blush pink label with hair-strand line art"},
]
