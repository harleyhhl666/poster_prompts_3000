def A(n, amt, unit, key=None, names=None):
    d = {"n": n, "amt": amt, "unit": unit, "nrv_key": key}
    if names is not None: d["names"] = names
    return d
def I(n, mg, us=None, active=True):
    d = {"n": n, "mg": mg, "us": us or n}
    if active: d["active"] = True
    return d

ITEMS = [
{"id": "s_multi_50plus", "sub_category": "50+ multivitamin", "regimes": ["US", "EU"],
 "names": ["50+ Multivitamin & Minerals", "Multivitamin 50+ with Lutein"],
 "form": "tablet", "pack": "bottle", "counts": [30, 90], "count_is_net": False, "price_eur": [5.0, 16.0],
 "dose": {"units": 1, "unit_word": "tablet", "directions": "Take 1 tablet daily with food."},
 "actives": [A("Vitamin A (as retinyl acetate)", 600, "µg", "vita"), A("Vitamin D3", 25, "µg", "vitd"),
             A("Vitamin E", 20, "mg", "vite"), A("Vitamin K1", 50, "µg", "vitk"), A("Vitamin C", 120, "mg", "vitc"),
             A("Thiamin", 2.2, "mg", "thiamin"), A("Riboflavin", 2.8, "mg", "riboflavin"), A("Niacin", 18, "mg", "niacin"),
             A("Vitamin B6", 4, "mg", "vitb6"), A("Folic acid", 400, "µg", "folate"), A("Vitamin B12", 25, "µg", "vitb12"),
             A("Biotin", 50, "µg", "biotin"), A("Pantothenic acid", 10, "mg", "pantothenic"), A("Calcium", 160, "mg", "calcium"),
             A("Magnesium", 100, "mg", "magnesium"), A("Zinc", 10, "mg", "zinc"), A("Copper", 1, "mg", "copper"),
             A("Manganese", 2, "mg", "manganese"), A("Selenium", 55, "µg", "selenium"), A("Chromium", 50, "µg", "chromium"),
             A("Iodine", 150, "µg", "iodine"), A("Lutein", 1, "mg", None)],
 "ingredients": [I("Calcium carbonate", 400), I("Magnesium oxide", 166),
                 I("Bulking agent: microcrystalline cellulose", 150, "Microcrystalline cellulose", False),
                 I("Vitamin C (L-ascorbic acid)", 120, "Ascorbic acid"), I("Vitamin E (dl-alpha tocopheryl acetate)", 40, "dl-Alpha tocopheryl acetate"),
                 I("Glazing agent: hydroxypropyl methylcellulose", 25, "Hypromellose", False),
                 I("Marigold extract (5% lutein)", 20, "Marigold flower extract (5% lutein)"), I("Nicotinamide", 18, "Niacinamide"),
                 I("Zinc oxide", 12.5), I("Calcium D-pantothenate", 11), I("Anti-caking agent: magnesium stearate", 10, "Magnesium stearate", False),
                 I("Manganese sulphate", 6.2, "Manganese sulfate"), I("Pyridoxine hydrochloride", 4.9), I("Riboflavin", 2.8),
                 I("Thiamin mononitrate", 2.8), I("Copper sulphate", 2.5, "Cupric sulfate"), I("Vitamin A (retinyl acetate)", 2.0, "Vitamin A acetate"),
                 I("Folic acid", 0.4), I("Chromium picolinate", 0.4), I("Potassium iodide", 0.2), I("Sodium selenite", 0.12),
                 I("Vitamin K1 (phytomenadione)", 0.05, "Phytonadione"), I("Biotin", 0.05),
                 I("Vitamin D3 (cholecalciferol)", 0.025, "Cholecalciferol"), I("Cyanocobalamin", 0.025)],
 "hero_ing": "Marigold extract (5% lutein)",
 "eu_claims": ["Vitamin B12 contributes to the reduction of tiredness and fatigue", "Vitamin D contributes to the maintenance of normal bones",
               "Vitamin D contributes to the maintenance of normal muscle function", "Vitamin B6 contributes to normal psychological function",
               "Riboflavin contributes to the maintenance of normal vision"],
 "us_claims": ["Supports healthy energy levels in adults 50+", "Supports bone health", "Supports healthy eyes and brain function"],
 "upgrade": ["Turns back the clock on ageing", "Keeps your memory sharp as a teenager's"],
 "selling": ["Tailored for adults over 50", "Iron-free formula", "With lutein", "High in vitamins D and B12"],
 "exag_subtle": ["Keeps your mind young", "Helps you stay active like you were 30"],
 "exag_strong": ["Prevents Alzheimer's and dementia", "Reverses age-related memory loss", "Lowers blood pressure without medication"],
 "unsub": ["Formulated with leading geriatricians", "Proven to add years to your life"],
 "attr_tamper": "Anti-ageing medical formula",
 "suitable": "Adults aged 50 and over",
 "not_suitable": "Not intended for children or pregnant women. Consult your doctor if taking anticoagulant medication (contains vitamin K).",
 "pop_tamper": "Ideal for all ages, including children and expectant mothers.",
 "extra_warnings": ["Contains vitamin K: consult your doctor if you take warfarin or other blood-thinning medication."],
 "shelf": [24, "months"], "shelf_tamper": [48, "months"],
 "storage": "Store below 25°C in a dry place. Keep lid tightly closed.", "allergens": [],
 "visual": "white bottle with navy label and silver 50+ badge, oblong beige tablets"},
]
