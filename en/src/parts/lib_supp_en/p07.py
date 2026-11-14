def A(n, amt, unit, key=None, names=None):
    d = {"n": n, "amt": amt, "unit": unit, "nrv_key": key}
    if names is not None: d["names"] = names
    return d
def I(n, mg, us=None, active=False):
    d = {"n": n, "mg": mg, "us": us or n}
    if active: d["active"] = True
    return d

ITEMS = [
{"id": "s_iron_liquid_tonic", "sub_category": "Vitamins & minerals", "regimes": ["US", "EU"],
 "names": ["Liquid Iron & B Vitamins Tonic", "Iron Tonic with Vitamin C & B12"],
 "form": "liquid", "pack": "bottle", "counts": [250, 500], "count_is_net": True, "price_eur": [9.0, 22.0],
 "dose": {"units": 20, "unit_word": "ml", "directions": "Take 10 ml twice daily (20 ml) before meals."},
 "actives": [A("Iron (as ferrous gluconate)", 14, "mg", "iron"), A("Vitamin C", 40, "mg", "vitc"),
             A("Thiamin", 1.1, "mg", "thiamin"), A("Riboflavin", 1.4, "mg", "riboflavin"),
             A("Vitamin B6", 1.4, "mg", "vitb6"), A("Vitamin B12", 2.5, "µg", "vitb12")],
 "ingredients": [I("Water", 13500), I("Fruit juice concentrates (pear, blackcurrant, orange)", 3200, "Fruit juice concentrates (pear, black currant, orange)"),
                 I("Fructose", 1500), I("Natural flavouring", 200, "Natural flavors"), I("Ferrous gluconate", 120, "Ferrous gluconate", True),
                 I("Acidity regulator: citric acid", 100, "Citric acid"), I("Rosehip extract", 50),
                 I("Vitamin C (L-ascorbic acid)", 40, "Ascorbic acid", True), I("Preservative: potassium sorbate", 20, "Potassium sorbate"),
                 I("Riboflavin 5'-phosphate", 1.9, "Riboflavin 5'-phosphate", True), I("Pyridoxine hydrochloride", 1.7, "Pyridoxine hydrochloride", True),
                 I("Thiamin hydrochloride", 1.4, "Thiamine hydrochloride", True), I("Cyanocobalamin", 0.0025, "Cyanocobalamin", True)],
 "hero_ing": "Rosehip extract",
 "eu_claims": ["Iron contributes to normal energy-yielding metabolism", "Iron contributes to normal formation of red blood cells and haemoglobin",
               "Riboflavin contributes to the normal metabolism of iron", "Vitamin B12 contributes to normal red blood cell formation"],
 "us_claims": ["Supports healthy blood", "Supports natural energy", "Easy-to-take liquid"],
 "upgrade": ["Restores blood iron instantly", "Liquid energy that floods your veins"],
 "selling": ["Gentle liquid formula", "Fruity blackcurrant taste", "No artificial colours", "Suitable for vegetarians"],
 "exag_subtle": ["Wakes up tired blood", "Feel the difference from the first spoonful"],
 "exag_strong": ["Cures anaemia in 10 days", "Treats chronic fatigue syndrome", "Replaces blood transfusions"],
 "unsub": ["Doctors' first choice for tired women", "Absorbed 3 times faster than tablets"],
 "attr_tamper": "Medicinal-strength herbal blood tonic",
 "suitable": "Adults",
 "not_suitable": "Not suitable for children under 12. Diabetics: contains natural fruit sugars. Consult your doctor if pregnant.",
 "pop_tamper": "Perfect for babies and toddlers - add to bottle feeds.",
 "extra_warnings": ["Contains iron: keep out of reach of children.", "Refrigerate after opening and use within 4 weeks."],
 "shelf": [18, "months"], "shelf_tamper": [36, "months"],
 "storage": "Store unopened below 25°C. Once opened, keep refrigerated and use within 4 weeks.", "allergens": [],
 "visual": "dark amber glass bottle, burgundy label with berries and a measuring cup"},
]
