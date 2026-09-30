# Food archetype schema (used by src/lib_food_*.py)

Each module defines `ARCHETYPES = [ {...}, ... ]`. Every dict:

```python
{
  "id": "dairy_uht_milk_hc",          # unique snake_case
  "sub_category": "乳制品",            # one of: 乳制品, 饮料, 零食, 烘焙, 调味品, 冲调谷物, 冷冻冷藏, 方便速食, 罐头, 肉制品, 蜂产品糖果, 米面粮油, 儿童食品, 代餐营养
  "product_type": "灭菌乳",            # 产品类型 exactly as printed on a Chinese label (e.g. 植物蛋白饮料 / 风味发酵乳 / 饼干 / 膨化食品 / 酿造酱油)
  "names": ["高钙低脂纯牛奶", "全脂纯牛奶"],   # product-name cores; brand is prepended by the engine. Must match the recipe.
  "form": "liquid" | "solid",
  "packages": [                        # realistic Chinese retail packs
     {"pack": "利乐砖盒", "net": "250mL", "count": 12, "unit_word": "盒", "price": [45.0, 79.0]},
  ],
  "recipes": [                         # 1–3 recipes; ingredient 'p' = % by mass added (should sum ~100, water included)
     {"ing": [
        {"n": "生牛乳", "p": 99.8, "a": ["乳"]},
        {"n": "碳酸钙", "p": 0.2},
      ],
      "nut": {"protein": 3.2, "fat": 1.2, "carb": 4.8, "sugar": 4.8, "sodium": 55, "calcium": 125},  # per 100 g / 100 mL
      "names": [0]                     # OPTIONAL: indexes into "names" this recipe fits (default: all)
     }
  ],
  "nut_keys": ["energy","protein","fat","carb","sodium","calcium"],   # rows shown; ALWAYS contains energy, protein, fat, carb, sodium (core 4+1); optional: sat, trans, sugar, lactose, fiber, calcium, vitc, iron, potassium, vitd, zinc, vita
  "basis": "100mL",                   # "100g" | "100mL" | "serving"
  "serving": None,                     # e.g. {"size": 30, "unit": "g", "label": "每份（30g）"} when basis == serving
  "claims_ok": ["低脂", "高钙"],       # nutrient content claims; engine re-validates against GB 28050 thresholds and drops failing ones
  "function_claim": "钙是骨骼和牙齿的主要成分，并维持骨密度。",  # GB 28050 Annex D standard phrase or None; only if matching content claim holds
  "selling": ["优质奶源", "口感醇厚", "180天常温保存"],  # non-health marketing copy (normal)
  "exag_subtle": ["每天一盒，有效增强骨骼强度"],     # mildly over-the-line claims (dataset-designed anomaly)
  "exag_strong": ["坚持饮用30天，告别骨质疏松", "中老年补钙首选，远离骨折风险"],  # clearly over the line, still realistic ad talk
  "shelf": [6, "月"],                 # [value, "月"|"天"]
  "shelf_tamper": [9, "月"],           # plausible-looking but wrong extended value
  "storage": "常温保存，避免阳光直射，开启后请立即饮用或2—6℃冷藏并于24小时内饮用完毕。",
  "storage_tamper": "常温保存",        # optional: wrong storage condition (e.g. chilled product labelled 常温) or None
  "usage": "开盒即饮，冷藏后风味更佳。",
  "standard": {"code": "GB 25190-2010", "verified": True},   # ONLY use the verified list below; else None (engine creates a fictional enterprise standard Q/...)
  "wrong_standard": "GB 19645-2010",   # a verified standard of a DIFFERENT category, for standard-category-mismatch anomalies, or None
  "attr_tamper": "有机纯牛奶",          # optional product-attribute misrepresentation text (e.g. 有机/儿童专用/保健食品) or None
  "population": "一般人群",             # 适宜人群 text if relevant, else None
  "visual": "白色利乐砖盒，蓝色草原与奶牛插画",       # short packaging look description (Chinese)
}
```

Hard rules
- Ingredient names must be real Chinese label names (白砂糖, 小麦粉, 植物油 / 棕榈油, 全脂乳粉, 食用盐, 麦芽糊精, 碳酸氢钠, 单，双甘油脂肪酸酯, 食用香精 …).
- Recipes with sugar/oil should contain at least one "healthy-sounding" hero ingredient (燕麦, 全麦粉, 奇亚籽, 坚果, 果粒, 可可, 膳食纤维/菊粉, 胶原蛋白肽, 乳清蛋白 …) whose `p` is LOWER than sugar or oil, so the engine can build ingredient-order tampering. Mark it with `"hero": True`.
- `a` (allergen categories) uses only: 麸质, 甲壳, 鱼, 蛋, 花生, 大豆, 乳, 坚果.  (GB 7718-2025 §4.12.1 eight categories.)
  Exempt per GB 7718-2025 D.4, do NOT tag: 精炼大豆油, 精炼花生油, 大豆磷脂/磷脂, 维生素E, 淀粉, 糊精, 麦芽糊精, 葡萄糖浆, 精炼鱼油, 鱼油来源DHA, 乳糖醇, 鱼明胶.
- Nutrition per 100 must be physically plausible (protein+fat+carb+fiber ≤ 100 for solids; liquids realistic).
- Claims must meet GB 28050-2011 Table C.1 (engine checks):  低脂 ≤3 g/100g or ≤1.5 g/100mL; 无/不含脂肪 ≤0.5;  无糖 sugar ≤0.5; 低糖 sugar ≤5;  高蛋白 ≥12 g/100g or ≥6 g/100mL; 蛋白质来源 ≥6 g/100g or ≥3 g/100mL;  高膳食纤维 ≥6 g/100g or ≥3 g/100mL; 膳食纤维来源 ≥3 g/100g or ≥1.5 g/100mL;  低钠 ≤120 mg; 高钙 ≥240 mg/100g or ≥120 mg/100mL; 钙来源 ≥120 mg/100g or ≥60 mg/100mL; 高维生素C ≥30 mg/100g or ≥15 mg/100mL; 低能量 ≤170 kJ/100g or ≤80 kJ/100mL.
  If you claim 无糖/低糖 you MUST include "sugar" in nut and nut_keys.
- GB 28050 Annex D function phrases allowed (use verbatim):
  蛋白质有助于组织的形成和生长。 / 钙是骨骼和牙齿的主要成分，并维持骨密度。 / 膳食纤维有助于维持正常的肠道功能。 / 维生素C有助于维持骨骼、牙龈的健康。 / 每日膳食中脂肪提供的能量比例不宜超过总能量的30%。 / 钠摄入过高有害健康。
- No real brands. No brand names in `names` (engine adds fictional brand).
- Verified real standards you MAY use (scope checked):
  GB 19645-2010 巴氏杀菌乳; GB 25190-2010 灭菌乳; GB 25191-2010 调制乳; GB 19302-2025 发酵乳(发酵乳和风味发酵乳); GB 19644-2024 乳粉; GB 7101-2022 饮料; GB 7099-2015 糕点、面包; GB 7100-2015 饼干; GB 2759-2015 冷冻饮品和制作料; GB 19295-2021 速冻面米与调制食品; GB 7098-2015 罐头食品; GB 14963-2011 蜂蜜; GB 2749-2015 蛋与蛋制品; GB 2730-2015 腌腊肉制品; GB 5420-2021 干酪; GB 25192-2022 再制干酪和干酪制品.
  Anything else → "standard": None.
