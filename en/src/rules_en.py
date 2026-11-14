"""Verified rule constants for the English (Europe / North America) part. Sources in en/taxonomy_en.md section 6.
EU: Reg (EU) 1169/2011 (Annex II allergens, Annex XIII NRV + RI, Annex XIV energy factors, Annex XV order);
    Reg (EC) 1924/2006 Annex (nutrition claims); Reg (EU) 432/2012 (authorised health claims).
US: 21 CFR 101.9 (DVs, rounding), 101.54 / 101.60 / 101.61 / 101.62 (nutrient content claims), 101.36, 101.93, 101.17(e).
"""

# EU Annex XIII Part A (adult NRV) - unit as in keys comment
EU_NRV = {"vita": 800, "vitd": 5, "vite": 12, "vitk": 75, "vitc": 80, "thiamin": 1.1, "riboflavin": 1.4, "niacin": 16,
          "vitb6": 1.4, "folate": 200, "vitb12": 2.5, "biotin": 50, "pantothenic": 6, "potassium": 2000, "chloride": 800,
          "calcium": 800, "phosphorus": 700, "magnesium": 375, "iron": 14, "zinc": 10, "copper": 1, "manganese": 2,
          "fluoride": 3.5, "selenium": 55, "chromium": 40, "molybdenum": 50, "iodine": 150}
# EU Annex XIII Part B reference intakes
EU_RI = {"energy_kj": 8400, "energy_kcal": 2000, "fat": 70, "sat": 20, "carb": 260, "sugar": 90, "protein": 50, "salt": 6}
# US DV adults & children >=4 (21 CFR 101.9(c)(8)(iv) and (c)(9))
US_DV = {"fat": 78, "sat": 20, "cholesterol": 300, "sodium": 2300, "carb_total": 275, "fibre": 28, "added_sugar": 50,
         "protein": 50, "vitd": 20, "calcium": 1300, "iron": 18, "potassium": 4700, "vita": 900, "vitc": 90, "vite": 15,
         "vitk": 120, "thiamin": 1.2, "riboflavin": 1.3, "niacin": 16, "vitb6": 1.7, "folate": 400, "vitb12": 2.4,
         "biotin": 30, "pantothenic": 5, "phosphorus": 1250, "iodine": 150, "magnesium": 420, "zinc": 11,
         "selenium": 55, "copper": 0.9, "manganese": 2.3, "chromium": 35, "molybdenum": 45, "chloride": 2300}
NUT_UNIT = {"vita": "µg", "vitd": "µg", "vite": "mg", "vitk": "µg", "vitc": "mg", "thiamin": "mg", "riboflavin": "mg",
            "niacin": "mg", "vitb6": "mg", "folate": "µg", "vitb12": "µg", "biotin": "µg", "pantothenic": "mg",
            "potassium": "mg", "chloride": "mg", "calcium": "mg", "phosphorus": "mg", "magnesium": "mg", "iron": "mg",
            "zinc": "mg", "copper": "mg", "manganese": "mg", "fluoride": "mg", "selenium": "µg", "chromium": "µg",
            "molybdenum": "µg", "iodine": "µg"}
NUT_LABEL = {"vita": "Vitamin A", "vitd": "Vitamin D", "vite": "Vitamin E", "vitk": "Vitamin K", "vitc": "Vitamin C",
             "thiamin": "Thiamin", "riboflavin": "Riboflavin", "niacin": "Niacin", "vitb6": "Vitamin B6",
             "folate": "Folic acid", "vitb12": "Vitamin B12", "biotin": "Biotin", "pantothenic": "Pantothenic acid",
             "potassium": "Potassium", "chloride": "Chloride", "calcium": "Calcium", "phosphorus": "Phosphorus",
             "magnesium": "Magnesium", "iron": "Iron", "zinc": "Zinc", "copper": "Copper", "manganese": "Manganese",
             "fluoride": "Fluoride", "selenium": "Selenium", "chromium": "Chromium", "molybdenum": "Molybdenum",
             "iodine": "Iodine"}

# Annex XIV energy conversion factors
def energy(n):
    kj = 17 * n["carb"] + 17 * n["protein"] + 37 * n["fat"] + 8 * n.get("fibre", 0) + 10 * n.get("polyols", 0)
    kcal = 4 * n["carb"] + 4 * n["protein"] + 9 * n["fat"] + 2 * n.get("fibre", 0) + 2.4 * n.get("polyols", 0)
    return kj, kcal

ALLERGEN_GROUPS = ["gluten", "crustaceans", "eggs", "fish", "peanuts", "soybeans", "milk", "nuts", "celery", "mustard",
                   "sesame", "sulphites", "lupin", "molluscs"]
GLUTEN = ["wheat", "rye", "barley", "oats", "spelt"]
NUTS = ["almond", "hazelnut", "walnut", "cashew", "pecan", "brazil", "pistachio", "macadamia"]
# US major food allergens (FALCPA + FASTER Act): map EU tag -> US "Contains" word (None = not a US major allergen)
def us_allergen_word(tag):
    g, _, sp = tag.partition(":")
    if g == "gluten":
        return "Wheat" if sp in ("wheat", "spelt") else None
    if g == "nuts":
        return {"almond": "Almonds", "hazelnut": "Hazelnuts", "walnut": "Walnuts", "cashew": "Cashews", "pecan": "Pecans",
                "brazil": "Brazil nuts", "pistachio": "Pistachios", "macadamia": "Macadamia nuts"}[sp]
    if g == "fish":
        return sp.capitalize() if sp else "Fish"
    if g == "crustaceans":
        return sp.capitalize() if sp else "Shellfish"
    return {"eggs": "Egg", "peanuts": "Peanuts", "soybeans": "Soy", "milk": "Milk", "sesame": "Sesame"}.get(g)

def valid_tag(tag):
    g, _, sp = tag.partition(":")
    if g not in ALLERGEN_GROUPS:
        return False
    if g == "gluten":
        return sp in GLUTEN
    if g == "nuts":
        return sp in NUTS
    if g in ("fish", "crustaceans", "molluscs"):
        return bool(sp)
    return sp == ""

# EU 1924/2006 Annex: claim -> test(per100 dict, form, kcal_per100)
def _pe(n, kcal):  # % energy from protein
    return 0 if kcal <= 0 else 4 * n["protein"] / kcal * 100

EU_CLAIMS = {
    "Low fat": lambda n, f, k: n["fat"] <= (3 if f == "solid" else 1.5),
    "Fat free": lambda n, f, k: n["fat"] <= 0.5,
    "Low saturated fat": lambda n, f, k: n["sat"] + n.get("trans", 0) <= (1.5 if f == "solid" else 0.75)
                                           and (n["sat"] + n.get("trans", 0)) * 9 <= 0.10 * max(k, 1e-9),
    "Low sugars": lambda n, f, k: n["sugar"] <= (5 if f == "solid" else 2.5),
    "Sugars free": lambda n, f, k: n["sugar"] <= 0.5,
    "No added sugars": lambda n, f, k: n.get("added_sugar", 0) == 0,
    "Low salt": lambda n, f, k: n["salt"] <= 0.3,          # 0.12 g sodium x 2.5
    "Source of fibre": lambda n, f, k: n.get("fibre", 0) >= 3 or (k > 0 and n.get("fibre", 0) / k * 100 >= 1.5),
    "High fibre": lambda n, f, k: n.get("fibre", 0) >= 6 or (k > 0 and n.get("fibre", 0) / k * 100 >= 3),
    "Source of protein": lambda n, f, k: _pe(n, k) >= 12,
    "High protein": lambda n, f, k: _pe(n, k) >= 20,
    "Low energy": lambda n, f, k: k <= (40 if f == "solid" else 20),
}
for _key, _nk in (("calcium", "calcium"), ("vitamin D", "vitd"), ("iron", "iron"), ("vitamin C", "vitc")):
    EU_CLAIMS["Source of " + _key] = (lambda nk: lambda n, f, k: n.get(nk, 0) >= EU_NRV[nk] * (0.15 if f == "solid" else 0.075))(_nk)
EU_CLAIMS["High in calcium"] = lambda n, f, k: n.get("calcium", 0) >= EU_NRV["calcium"] * (0.30 if f == "solid" else 0.15)

SUGAR_WORDS = ["sugar", "syrup", "honey", "dextrose", "glucose", "fructose", "sucrose", "maltodextrin", "juice concentrate",
               "concentrated", "molasses", "nectar", "treacle", "invert"]
