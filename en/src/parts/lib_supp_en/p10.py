def A(n, amt, unit, key=None, names=None):
    d = {"n": n, "amt": amt, "unit": unit, "nrv_key": key}
    if names is not None: d["names"] = names
    return d
def I(n, mg, us=None, active=False):
    d = {"n": n, "mg": mg, "us": us or n}
    if active: d["active"] = True
    return d

ITEMS = [
{"id": "s_prenatal_dha_iron", "sub_category": "Prenatal", "regimes": ["US", "EU"],
 "names": ["Prenatal Multivitamin + DHA Softgel", "Pregnancy Complete with Iron & Omega-3 DHA"],
 "form": "softgel", "pack": "bottle", "counts": [30, 60], "count_is_net": False, "price_eur": [9.0, 22.0],
 "dose": {"units": 1, "unit_word": "softgel", "directions": "Take 1 softgel daily with your main meal."},
 "actives": [A("Vitamin D3", 10, "µg", "vitd"), A("Vitamin C", 70, "mg", "vitc"), A("Vitamin B6", 1.9, "mg", "vitb6"),
             A("Folic acid", 400, "µg", "folate"), A("Vitamin B12", 2.6, "µg", "vitb12"), A("Iron (as ferrous fumarate)", 17, "mg", "iron"),
             A("Zinc", 10, "mg", "zinc"), A("Iodine", 150, "µg", "iodine"), A("DHA (docosahexaenoic acid)", 250, "mg", None),
             A("EPA (eicosapentaenoic acid)", 50, "mg", None)],
 "ingredients": [I("Fish oil concentrate (FISH - anchovy, sardine)", 500, "Fish oil concentrate (anchovy, sardine)", True),
                 I("Capsule shell (bovine gelatine, glycerol, colour: iron oxides)", 350, "Softgel (bovine gelatin, glycerin, iron oxides)"),
                 I("Vitamin C (L-ascorbic acid)", 70, "Ascorbic acid", True), I("Ferrous fumarate", 52, "Ferrous fumarate", True),
                 I("Thickener: yellow beeswax", 40, "Yellow beeswax"), I("Emulsifier: SOYA lecithin", 20, "Soy lecithin"),
                 I("Zinc oxide", 12.5, "Zinc oxide", True), I("Pyridoxine hydrochloride", 2.3, "Pyridoxine hydrochloride", True),
                 I("Folic acid", 0.4, "Folic acid", True), I("Potassium iodide", 0.2, "Potassium iodide", True),
                 I("Vitamin D3 (cholecalciferol)", 0.01, "Cholecalciferol", True), I("Cyanocobalamin", 0.0026, "Cyanocobalamin", True)],
 "hero_ing": "Folic acid",
 "eu_claims": ["Folate contributes to maternal tissue growth during pregnancy", "Iron contributes to normal formation of red blood cells and haemoglobin",
               "Iodine contributes to normal cognitive function", "DHA contributes to maintenance of normal brain function",
               "Vitamin D contributes to the maintenance of normal bones"],
 "us_claims": ["Supports a healthy pregnancy", "DHA supports baby's brain and eye development", "Supports healthy blood for mum"],
 "upgrade": ["Guarantees a genius baby", "Builds your baby's brain twice as fast"],
 "selling": ["All-in-one multivitamin and DHA softgel", "No vitamin A (retinol)", "With 400µg folic acid and iodine", "Gentle on the stomach"],
 "exag_subtle": ["Gives your baby the best start, guaranteed", "No morning sickness"],
 "exag_strong": ["Prevents pre-eclampsia and premature birth", "Prevents birth defects", "Cures pregnancy anaemia"],
 "unsub": ["Recommended by 9 out of 10 obstetricians", "Proven to raise baby IQ"],
 "attr_tamper": "Prescription prenatal formula",
 "suitable": "Women trying to conceive, pregnant and breastfeeding women",
 "not_suitable": "Not suitable for children or men. Do not take with other multivitamins. Not suitable if allergic to fish or soy.",
 "pop_tamper": "Safe for the whole family, including toddlers.",
 "extra_warnings": ["Contains iron: accidental overdose of iron-containing products is a leading cause of fatal poisoning in children under 6.",
                    "Contains fish and soy."],
 "shelf": [24, "months"], "shelf_tamper": [48, "months"],
 "storage": "Store below 25°C in a dry place.", "allergens": ["fish:anchovy", "fish:sardine", "soybeans"],
 "visual": "soft lilac bottle with bump silhouette, opaque brown softgels"},
]
