# Food archetype schema (en/src/lib_food_en_*.py)

Each module defines `ARCHETYPES = [ {...}, ... ]`. All text in English (UK spelling by default; give US
spellings via the optional `"us"` key). Products must be realistic for Europe / North America retail.

```python
{
 "id": "dairy_greek_yogurt",            # unique snake_case, prefix by module (e.g. "a_", "b_", "c_")
 "sub_category": "Dairy & alternatives", # enum, see below
 "legal_name": "Greek style natural yogurt",   # EU 'name of the food' / US statement of identity (descriptive)
 "names": ["Greek Style Natural Yogurt", "Greek Style Yogurt with Honey"],  # product-name cores, no brand
 "form": "solid",                       # "solid" | "liquid"
 "origin_ok": ["GR", "CY", "BG", "UK", "US"],  # ISO2 countries where it is plausibly MADE (Europe/NA only)
 "markets": ["UK", "IE", "MT", "US"],   # retail label markets it fits (subset of UK, IE, MT, US)
 "packages": [ {"pack": "pot", "net": 500, "unit": "g", "count": 1, "price_eur": [1.8, 3.5]} ],
 # pack enum: box, bag, bottle, can, carton, jar, pot, tub, tray, pouch, wrapper, multipack, tin
 # net = per unit; count = units sold together; price_eur = realistic shelf price range for the whole pack
 "recipes": [ {
    "ing": [ {"n": "Pasteurised cow's MILK", "p": 95.0, "a": ["milk"], "us": "Pasteurized cultured milk"},
             {"n": "Honey", "p": 4.9, "hero": True, "quid": True},
             {"n": "Live cultures", "p": 0.1} ],
    "nut": {"fat": 5.0, "sat": 3.4, "trans": 0.1, "carb": 4.0, "sugar": 4.0, "added_sugar": 0.0,
            "fibre": 0.0, "protein": 9.0, "salt": 0.1, "cholesterol": 15, "calcium": 110,
            "iron": 0.0, "potassium": 140, "vitd": 0.0},   # per 100 g (solids) or 100 ml (liquids)
    "names": [0] } ],                  # OPTIONAL indexes into names this recipe fits (default all)
 "eu_extra": ["fibre", "calcium"],      # optional extra EU rows: subset of fibre, calcium, iron, vitd, vitc, potassium
 "serving": {"g": 150, "us_household": "2/3 cup", "eu_label": "150g"},
 "claims_ok": ["High protein", "Source of calcium"],   # vocab below; engine re-checks thresholds, drops failures
 "health_claim": "Calcium is needed for the maintenance of normal bones",  # VERBATIM from refs/eu432_claims.json or None
 "selling": ["Thick and creamy", "Strained for a rich texture", "Made with British milk", "Perfect with granola"],  # >=4
 "exag_subtle": ["Supports strong bones for life", "Keeps your gut happy every day"],                         # >=2
 "exag_strong": ["Clinically proven to prevent osteoporosis", "Cures bloating in 7 days", "Lowers cholesterol naturally"],  # >=3
 "shelf": [21, "days"],                 # [value, "days"|"months"]
 "shelf_tamper": [45, "days"],          # plausible-looking but wrong longer value, same unit
 "date_type": "use_by",                 # "use_by" (highly perishable chilled) | "best_before"
 "storage": "Keep refrigerated at {fridge}. Once opened, consume within 3 days.",
 "storage_tamper": "Store in a cool, dry place.",   # wrong condition for chilled/frozen items, else None
 "prep": "Serve chilled.",              # or None
 "animal_origin": True,                 # needs EU identification (oval) mark: meat, fish, dairy, egg products
 "attr_tamper": "Organic",              # false attribute text (Organic / Clinically tested / Kids' formula / Medical grade) or None
 "population": None,                    # e.g. "Suitable from 12 months" for kids items, else None
 "may_contain": ["nuts:hazelnut"],      # precautionary allergens (not in recipe) or []
 "visual": "white plastic pot with blue border, spoonful of thick yogurt and drizzle of honey",
}
```

## Enums
sub_category: Dairy & alternatives | Beverages | Breakfast cereals | Snacks | Confectionery | Bakery & biscuits |
Spreads & sauces | Ready meals & frozen | Meat, fish & deli | Canned & jarred | Pasta, rice & grains |
Baby & kids | Meal replacement & sports | Seasonal

Allergen tags (`a`): gluten:wheat, gluten:rye, gluten:barley, gluten:oats, gluten:spelt, crustaceans:<species>,
eggs, fish:<species>, peanuts, soybeans, milk, nuts:almond|hazelnut|walnut|cashew|pecan|brazil|pistachio|macadamia,
celery, mustard, sesame, sulphites, lupin, molluscs:<species>   (EU Reg 1169/2011 Annex II, 14 groups)

claims_ok vocab (EU Reg 1924/2006 Annex): Low fat, Fat free, Low saturated fat, Low sugars, Sugars free,
No added sugars, Low salt, Source of fibre, High fibre, Source of protein, High protein, Source of calcium,
High in calcium, Source of vitamin D, Source of iron, Source of vitamin C, Low energy.
"No added sugars" only if no sugar/syrup/honey/juice-concentrate ingredient. Claims needing a micronutrient
require that key in the recipe `nut` and in `eu_extra`.

## Hard rules (validator enforces most)
- Ingredient `p` = % by mass at time of use, descending order, sum 90–110 (water included).
- EU allergen emphasis is written IN CAPITALS inside `n` (e.g. "Wholegrain OAT flakes", "Butter (MILK)",
  "emulsifier: SOYA lecithins"). Every tagged ingredient must contain an all-caps allergen word; untagged ingredients
  must NOT contain all-caps words (E-numbers like E322 are fine). Exempt per Annex II, do not tag/capitalise:
  wheat glucose syrup, wheat maltodextrin, barley glucose syrup, fully refined soybean oil, soy tocopherols, lactitol.
- Sweet/fatty recipes need >=1 `hero` ingredient (oats, wholegrain, nuts, fruit, cocoa, chia, inulin, protein...) with
  `p` LOWER than the first ingredient, so ingredient-order tampering is possible. Put `quid: True` on ingredients named
  in the product name or emphasised (Art 22 QUID) — the engine prints their %.
- Nutrition plausible: sugar<=carb, added_sugar<=sugar, sat+trans<=fat, protein+fat+carb+fibre<=100 (solids).
  `carb` = available carbohydrate (EU definition, excludes fibre). salt in g, cholesterol/calcium/iron/potassium in mg,
  vitd in µg. No added sugar ingredient -> added_sugar 0.
- `health_claim` only verbatim from refs/eu432_claims.json and only if its nutrient condition can hold.
- 3–4 packages, 1–3 recipes, names must match recipe (flavour in name must be an ingredient).
- No real brands, retailers, trademarks (e.g. Nutella, Weetabix, Oreo, Pringles, Kinder) anywhere.
