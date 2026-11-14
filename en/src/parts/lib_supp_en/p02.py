def A(n, amt, unit, key=None, names=None):
    d = {"n": n, "amt": amt, "unit": unit, "nrv_key": key}
    if names is not None: d["names"] = names
    return d
def I(n, mg, us=None, active=True):
    d = {"n": n, "mg": mg, "us": us or n}
    if active: d["active"] = True
    return d

ITEMS = [
{"id": "s_az_multi_iron", "sub_category": "Vitamins & minerals", "regimes": ["US", "EU"],
 "names": ["A-Z Multivitamins & Minerals", "Complete Multivitamin with Iron"],
 "form": "tablet", "pack": "blister box", "counts": [30, 90], "count_is_net": False, "price_eur": [4.0, 14.0],
 "dose": {"units": 1, "unit_word": "tablet", "directions": "Take 1 tablet daily with breakfast and a glass of water."},
 "actives": [A("Vitamin A (as retinyl acetate)", 800, "µg", "vita"), A("Vitamin D3", 10, "µg", "vitd"),
             A("Vitamin E", 12, "mg", "vite"), A("Vitamin K1", 75, "µg", "vitk"), A("Vitamin C", 80, "mg", "vitc"),
             A("Thiamin", 1.1, "mg", "thiamin"), A("Riboflavin", 1.4, "mg", "riboflavin"), A("Niacin", 16, "mg", "niacin"),
             A("Vitamin B6", 1.4, "mg", "vitb6"), A("Folic acid", 200, "µg", "folate"), A("Vitamin B12", 2.5, "µg", "vitb12"),
             A("Biotin", 50, "µg", "biotin"), A("Pantothenic acid", 6, "mg", "pantothenic"), A("Calcium", 120, "mg", "calcium"),
             A("Magnesium", 60, "mg", "magnesium"), A("Iron", 14, "mg", "iron"), A("Zinc", 10, "mg", "zinc"),
             A("Copper", 1, "mg", "copper"), A("Manganese", 2, "mg", "manganese"), A("Selenium", 55, "µg", "selenium"),
             A("Chromium", 40, "µg", "chromium"), A("Molybdenum", 50, "µg", "molybdenum"), A("Iodine", 150, "µg", "iodine")],
 "ingredients": [I("Calcium carbonate", 300), I("Bulking agent: microcrystalline cellulose", 260, "Microcrystalline cellulose", False),
                 I("Magnesium oxide", 100), I("Vitamin C (L-ascorbic acid)", 80, "Ascorbic acid"), I("Ferrous fumarate", 43),
                 I("Vitamin E (dl-alpha tocopheryl acetate)", 24, "dl-Alpha tocopheryl acetate"),
                 I("Glazing agent: hydroxypropyl methylcellulose", 20, "Hypromellose", False), I("Nicotinamide", 16, "Niacinamide"),
                 I("Zinc oxide", 12.5), I("Anti-caking agent: magnesium stearate", 10, "Magnesium stearate", False),
                 I("Anti-caking agent: silicon dioxide", 8, "Silicon dioxide", False), I("Calcium D-pantothenate", 6.5),
                 I("Manganese sulphate", 6.2, "Manganese sulfate"), I("Vitamin A (retinyl acetate)", 2.8, "Vitamin A acetate"),
                 I("Copper sulphate", 2.5, "Cupric sulfate"), I("Pyridoxine hydrochloride", 1.7), I("Riboflavin", 1.6),
                 I("Thiamin mononitrate", 1.4), I("Folic acid", 0.2), I("Potassium iodide", 0.2), I("Chromium chloride", 0.15),
                 I("Sodium molybdate", 0.13), I("Sodium selenite", 0.12), I("Vitamin K1 (phytomenadione)", 0.075, "Phytonadione"),
                 I("Biotin", 0.05), I("Vitamin D3 (cholecalciferol)", 0.01, "Cholecalciferol"), I("Cyanocobalamin", 0.0025)],
 "hero_ing": "Biotin",
 "eu_claims": ["Iron contributes to the reduction of tiredness and fatigue", "Vitamin D contributes to the normal function of the immune system",
               "Vitamin B12 contributes to normal energy-yielding metabolism", "Zinc contributes to the normal function of the immune system",
               "Biotin contributes to the maintenance of normal skin"],
 "us_claims": ["Supports energy metabolism", "Supports immune health", "Helps fill nutritional gaps in the diet"],
 "upgrade": ["Unlocks all-day energy and total immunity", "Everything your body needs in one tablet - no healthy diet required"],
 "selling": ["23 vitamins and minerals", "Once-daily tablet", "Easy-swallow coated tablet", "3-month supply in the large pack"],
 "exag_subtle": ["Never feel tired again", "Covers everything your diet is missing"],
 "exag_strong": ["Prevents heart disease and cancer", "Cures anaemia within a week", "Replaces the need for a balanced diet and medication"],
 "unsub": ["Clinically proven complete nutrition", "Britain's most trusted multivitamin"],
 "attr_tamper": "Medical-grade prescription formula",
 "suitable": "Adults and teenagers over 12 years",
 "not_suitable": "Not suitable for children under 12 or during pregnancy (contains vitamin A). Do not take with other iron or vitamin A supplements.",
 "pop_tamper": "Suitable for children of all ages and recommended during pregnancy.",
 "extra_warnings": ["Contains iron: keep out of sight and reach of young children."],
 "shelf": [24, "months"], "shelf_tamper": [48, "months"],
 "storage": "Store below 25°C in a dry place.", "allergens": [],
 "visual": "white carton with rainbow alphabet A-Z band, foil blister of oval orange tablets"},
]
