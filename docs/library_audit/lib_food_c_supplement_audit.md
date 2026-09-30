# Audit log — lib_food_c.py / lib_supplement.py (variant-truth audit)

Goal: every printed string (name, selling/normal_copy, visual, claims, nutrition, components, cautions, suitable, exag_*, attr/population tamper)
must be true for EVERY name × recipe variant the engine can pick.
Validator: `python src/validate_libs.py lib_food_c lib_supplement` → OK (29 archetypes, 41 supplements; ids, order and schema keys unchanged).

Entries changed: **lib_food_c 27 / 29**, **lib_supplement 20 / 41** (47 total).

## lib_supplement.py
| id | fix |
|---|---|
| vc_chewable | name “（草莓味）” removed (only 甜橙粉 in raw) → “维生素C咀嚼片” |
| multivitamin_mineral_tablet | “（男士型）” removed (formula/suitable are generic adult) |
| vc_effervescent_drink | type consistency: dosage_form “固体饮料（泡腾片）”, names “维生素C泡腾片固体饮料…”, matches caution “本品为固体饮料（泡腾片）”; 蜜桃味 removed (only 柠檬粉) |
| calcium_vd_tablet | visual “牛奶滴” removed (no milk ingredient) |
| fish_oil_softgel | “高纯度鱼油软胶囊” → “鱼油软胶囊” (EPA+DHA 300 mg/1 g ≈30%) |
| algae_dha_gel_candy | nutrition per-粒 “脂肪0.4g/能量19kJ” replaced by plausible per-100g oil-gummy values (fat 48 g); kid cartoon visual kept → suitable “3岁以上儿童及成人”, cautions add “3岁以下儿童请勿食用”, 看护 line phrased for children |
| probiotic_solid_drink | adult product: “肠道卡通” → “肠道线条” |
| oligo_fiber_laxative_powder | dosage_form 粉剂 vs name “颗粒” → names both “…粉” |
| whey_soy_protein_powder | visual “大罐/附量勺” removed (spec also has 10 g 袋装) |
| sport_whey_protein | recipe has 可可粉 only → “香草味” name replaced by chocolate variant; dosage_form 粉剂 (a protein powder, not 固体饮料); visual “大桶” generalised (spec also 条袋) |
| lutein_pressed_candy | adult product: “卡通眼睛” → “眼睛线条” |
| fiber_solid_drink | nutrition: carb 8.9 g + fiber 7.5 g in a 10 g sachet was >100 %; carb 1.4 g, energy 86 kJ |
| fruit_veg_enzyme_drink | raw “复合果蔬汁” → “复合果蔬发酵汁” (both raw & tamper, still exact permutation) so “发酵饮品” name is backed; usage “每日1瓶” → “每日30mL” (spec includes 500 mL bottle); “小瓶便携”/“小玻璃瓶” removed |
| gaba_sleep_candy | “清甜奶香” removed (no dairy); “薰衣草” visual removed (not in raw) |
| kids_calcium_zinc_chewable | “（草莓味）” name (no strawberry) → “儿童钙锌维生素D咀嚼片” |
| kids_vd3_softgel | “维生素AD软胶囊” name (no vitamin A in raw/components) → “儿童维生素D3软胶囊” |
| kids_gummy_candy | “多种维生素凝胶糖果” (only vit C) → “维生素C乳钙凝胶糖果（水果味）”; “草莓味” (only 苹果汁) → “苹果味”; suitable “3岁以上儿童及成人” to match kids visual |
| iron_oral_liquid | “当归…” name (no 当归 in raw) → “枸杞红枣铁口服液” |
| vc_zinc_immune_tablet | dosage 咀嚼片 vs name “维生素C锌片” → “维生素C锌咀嚼片（樱桃味）” |
| lactoferrin_igy_drink | “调制乳粉固体饮料” (a different product category) → “乳铁蛋白乳清蛋白固体饮料” |

Checked and kept: health_function rules (注册 = exact 24-list item, 备案 = “补充…”, 普通食品 = None) untouched; every hero_first_tamper verified as exact permutation of raw_materials; all exag/attr/population_tamper lines only reference present ingredients.

## lib_food_c.py
Fix categories and entries:
- **Recipe/name mismatch (restrict names or add recipe)**
  - cond_hotpot_base: shared selling/exag/visual were 麻辣/重庆 and wrong for 番茄 variant → neutral text; 郫县豆瓣/汉源花椒 (origin) → 豆瓣酱/花椒.
  - instant_self_heating_hotpot: 素食 recipe now uses “植物油火锅底料” (no 牛油); “大块牛肉” exag → 腐竹.
  - instant_noodle_fried: added 老坛酸菜 recipe (酸菜 hero) bound to name 1; recipe 0 bound to 红烧牛肉面; “红烧汤底” selling and “大块牛肉” visual removed; 牛骨 → 牛肉汤底.
  - can_luncheon_meat: added 黑胡椒 recipe for name 1 (“黑椒” → “黑胡椒午餐肉罐头”).
  - oil_blended: 橄榄油 name was bound to the recipe WITHOUT olive oil → recipe name indexes swapped; olive/“物理压榨” text removed from shared copy; attr_tamper no longer references olive.
  - egg_braised_egg: “溏心卤蛋” (texture not in recipe/usage) → “酱香卤蛋”.
  - grain_mixed_rice: “杂粮饭” (ready rice) → “杂粮米”; 燕麦米 tagged 麸质 allergen.
  - grain_whole_wheat_noodle: product_type “挂面（全麦挂面）” was false for 荞麦 variant → “挂面”; 全麦/荞麦-specific shared copy → 粗粮.
  - instant_noodle_nonfried: “添加荞麦/全麦粉”, “酱包”, “荞麦降血糖”, “纯荞麦面” → variant-neutral; usage covers both 拌面/汤面.
  - frozen_tangyuan / frozen_ice_cream / frozen_popsicle / frozen_pizza / mr_meal_biscuit / mr_instant_oat_porridge / chilled_oat_rice_ball: variant-specific words in shared copy (黑芝麻, 香草荚, 绿豆, 牛肉, 燕麦片, 紫薯, 红豆薏米, 燕麦加鸡胸, 金枪鱼DHA) neutralised; mr_meal_biscuit “独立小包” and porridge “杯盖/一杯” fixed for bag packs.
- **Geographic origin claims removed**: cond_ketchup (新疆番茄), can_yellow_peach (砀山), cond_hotpot_base (重庆/郫县/汉源), frozen_ice_cream (进口稀奶油), instant_luosifen (“广西柳州” → “柳州风味”, 柳州风情 visual removed), meat_cantonese_sausage (names → “广式风味腊肠/甜腊肠”, selling “广式传统风味” → “传统腊味风味”), meat_ham_sausage_chilled (“德式” → “德式风味”).
- **Season/occasion-bound copy removed**: can_yellow_peach (新鲜采摘，当季封罐), frozen_ice_cream (夏日/夏天), frozen_popsicle (夏天), frozen_tangyuan (团圆佳节), meat_cantonese_sausage (年味/冬季/冬天).
- **Unverifiable/process claims**: frozen_pizza “手工拍饼”, chilled_oat_rice_ball “当日现做”, cond_salad_mayo “挤挤瓶设计” (1 kg 袋装 exists), meat_chicken_breast_rte & mr_shake_powder numeric “每袋约…g蛋白质” (not true for every pack; engine would drop) → reworded.
- **Nutrition plausibility**: mr_shake_powder recipe 0 calcium 260 with no calcium source → 180 (dairy only; 高钙 claim auto-drops for this variant); recipe 1 with 1.5 % 碳酸钙 → 720 mg; usage no longer says “1袋” (500 g 罐 pack).
- **exag referencing absent ingredients**: cond_oyster_sauce (补锌 w/o zinc row), instant_luosifen (胶原蛋白), frozen_dumpling (香菇多糖 on 玉米 variant).
- **Ingredient order (descending)**: cond_soy_sauce_premium (食用盐 11.5 before 小麦 8), chilled_oat_rice_ball r1 (甜玉米粒/白砂糖/海苔), mr_meal_biscuit r0 (水 before 全蛋液).

Checked and kept: “重庆风味”-type flavour styles removed only where tied to a wrong variant; brewery-made 酱/酱油 fine; all verified standards unchanged; claims_ok re-validated by the engine.

Smoke test: `food.make_food_spec` and `scenes_other.make_supp_spec` run for every entry/name variant; selling/visual/nutrition printed and reviewed.
