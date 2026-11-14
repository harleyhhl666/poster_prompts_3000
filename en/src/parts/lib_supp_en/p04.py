def A(n, amt, unit, key=None, names=None):
    d = {"n": n, "amt": amt, "unit": unit, "nrv_key": key}
    if names is not None: d["names"] = names
    return d
def I(n, mg, us=None, active=False):
    d = {"n": n, "mg": mg, "us": us or n}
    if active: d["active"] = True
    return d

ITEMS = [
{"id": "s_iron_vitc_gentle", "sub_category": "Vitamins & minerals", "regimes": ["US", "EU"],
 "names": ["Gentle Iron 14mg with Vitamin C", "Gentle Iron 20mg + Vitamin C"],
 "form": "capsule", "pack": "blister box", "counts": [30, 90], "count_is_net": False, "price_eur": [4.5, 13.0],
 "dose": {"units": 1, "unit_word": "capsule", "directions": "Take 1 capsule daily with water, ideally between meals."},
 "actives": [A("Iron (as ferrous bisglycinate)", 14, "mg", "iron", [0]), A("Iron (as ferrous bisglycinate)", 20, "mg", "iron", [1]),
             A("Vitamin C (as L-ascorbic acid)", 80, "mg", "vitc")],
 "ingredients": [I("Bulking agent: microcrystalline cellulose", 150, "Microcrystalline cellulose"),
                 I("Ferrous bisglycinate", 100, "Ferrous bisglycinate chelate", True),
                 I("Capsule shell: hydroxypropyl methylcellulose", 95, "Vegetable capsule (hypromellose)"),
                 I("Vitamin C (L-ascorbic acid)", 80, "Ascorbic acid", True), I("Anti-caking agent: magnesium stearate", 5, "Magnesium stearate")],
 "hero_ing": "Vitamin C (L-ascorbic acid)",
 "eu_claims": ["Iron contributes to the reduction of tiredness and fatigue", "Iron contributes to normal formation of red blood cells and haemoglobin",
               "Iron contributes to normal oxygen transport in the body", "Vitamin C increases iron absorption"],
 "us_claims": ["Supports healthy red blood cell formation", "Supports energy levels", "Gentle on the stomach"],
 "upgrade": ["Banishes tiredness for good", "Rebuilds your blood in days"],
 "selling": ["Gentle, non-constipating bisglycinate form", "With vitamin C for absorption", "Vegan capsule", "Once daily"],
 "exag_subtle": ["Ends tiredness and fatigue", "Restores your energy in a week"],
 "exag_strong": ["Cures iron-deficiency anaemia without a doctor", "Treats heavy-period anaemia", "Replaces iron infusions"],
 "unsub": ["Clinically proven 4x better absorption", "Recommended by haematologists"],
 "attr_tamper": "Prescription-strength iron",
 "suitable": "Adults, particularly women of child-bearing age",
 "not_suitable": "Not suitable for children. Do not take if you have haemochromatosis or are taking other iron supplements without medical advice.",
 "pop_tamper": "Safe for children and babies; take as many as you need.",
 "extra_warnings": ["Contains iron: accidental overdose of iron-containing products is a leading cause of fatal poisoning in children under 6."],
 "shelf": [24, "months"], "shelf_tamper": [48, "months"],
 "storage": "Store below 25°C in a dry place.", "allergens": [],
 "visual": "burgundy carton with red droplet icon, silver blister of red capsules"},
]
