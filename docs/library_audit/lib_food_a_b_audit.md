# Audit log: lib_food_a / lib_food_b (recipe-truth audit)

Rule applied: every name / selling / exag / visual / claims / product_type / population line must be true for every
recipe × package of its archetype. Fixes = generic rewrite, recipe `names` restriction, new recipe, or archetype split.
Global conventions:
- All geographic-origin wording removed (北纬/赣南/西湖/东北/云南/内蒙古/福建/岭南/广式/澳洲/西非/东南亚/北欧/希腊…).
- Season-bound copy removed (中秋…); no summer copy existed after audit.
- Real-brand slogans / trade dress removed (扭一扭舔一舔, blue milk-splash sandwich cookie, red small lactic bottle, AD钙 pink label,
  red-can gold herbal tea, blue walnut can + brain, silver-blue energy can, 怕上火, 经常用脑, 咖啡大师, 希腊蓝顶).
- 低钠 dropped where sodium is ~0 (sodium-free products) or where it is odd (electrolyte drink); kept where sodium is genuinely 20–120 mg.
- Pack-specific copy (小瓶装/独立小包/铁盒/罐/袋/礼盒) removed when any package of the archetype contradicts it.
- Numeric nutrient copy (每杯10g蛋白, 一片11mg VC, 一支16g蛋白) removed (pack-size dependent).

Archetype counts: lib_food_a 24 → 28 (4 splits), lib_food_b 33 → 33.

## lib_food_a
- **dairy_uht_milk**: '高钙低脂纯牛奶' recipe had 碳酸钙 (not allowed in 灭菌乳/纯牛奶) → renamed '低脂纯牛奶', raw-milk-only recipe (Ca 122, 高钙 still engine-checked); removed '北纬40°牧场' origin claim, numeric protein line, and '六层无菌包装' (false for 屋顶盒 pack).
- **dairy_modified_milk**: '真实燕麦颗粒口感'/'添加维生素D' only true for one recipe each → replaced with generic lines; visual '燕麦穗' removed (wrong for 儿童成长/核桃花生 recipes).
- **dairy_flavored_yogurt_chilled**: '真实果粒' false for 原味 recipe; '可以用勺吃' false for PET bottle pack; visual '粉色封口+草莓' only fits strawberry → generic; R0 protein 3.1→3.5 (milk+1% whey protein).
- **dairy_greek_yogurt**: split: sugared blueberry recipe moved to new dairy_greek_yogurt_flavored (product_type 风味发酵乳; plain stays 发酵乳); dropped '希腊' style/origin wording from names+visual; removed '3倍浓缩' (recipe is not strained) and numeric protein copy; protein 8.0→6.6 to match milk+4% MPC.
- **dairy_greek_yogurt_flavored**: NEW (split from dairy_greek_yogurt): 风味发酵乳, claims only 钙来源 (no 低糖/蛋白质来源 at 11 g sugar / 5.8 g protein), selling without '无添加蔗糖'.
- **dairy_cheese_stick**: protein 9.5/8.8→13.5/12.8 (32% 干酪+7% 全脂乳粉+5% 浓缩牛奶蛋白粉 cannot give <10 g); '卡通造型' → '棒状造型'.
- **dairy_milk_powder**: name '中老年高钙低脂奶粉' had 6 g fat (低脂 false) → '中老年高钙高蛋白奶粉'; removed '进口奶源' origin claim, '添加维生素D与锌' (no zinc in 学生 recipe, no vitD row), '独立条装' (only one pack is sticks); population → '3岁以上人群'; nutrition recomputed (R0 protein 20/carb 56, R1 fat 6.5/carb 47).
- **dairy_milk_beverage**: '酸酸甜甜' false for 原味 recipe (no acid); '添加维生素A、D'/'维生素AD' exag only fit AD recipe; '小瓶装' false for 250mL 利乐砖; visual white bottle+pink label+'AD钙' = real-brand trade dress → neutral cow/milk-wave look.
- **dairy_milk_tablet**: removed '内蒙古草原奶源' origin claim and '便携小包装' (false for 160g bag/300g can); visual dropped '草原' and '塑料袋' (can pack).
- **dairy_ambient_yogurt**: '真实黄桃果粒与燕麦' only for one recipe; '节日礼盒装' no such pack; exag '富含活性益生菌' false for heat-treated product; visual Greek blue-dome look (real-brand trade dress) → neutral.
- **bev_oat_drink**: name '（咖啡大师）' = real-brand product name → '（咖啡适用型）'; removed '北欧工艺' origin claim and Nordic-style visual; 'β-葡聚糖' exag only in one recipe → '燕麦膳食纤维'; '咖啡拉花好搭档' → generic; dropped 低钠 claim.
- **bev_soy_milk**: removed '东北' origin claim; exag '黑豆补肾' referenced 黑豆 absent in 2 recipes → generic; dropped 低钠.
- **bev_walnut_milk**: removed '云南' origin claim; exag '经常用脑…' = real-brand slogan, blue can + brain visual = real-brand trade dress → neutral; usage/storage said '连罐/开罐' but a 利乐砖 pack exists → generic; dropped 低钠.
- **bev_fruit_juice_drink**: '果汁含量≥10%' false for mango recipe (4% 芒果浆); '真实果肉粒' only true for orange; '聚会家庭分享装' only for 1.25L; exag '5个鲜橙' → '5个鲜果'; orange-only visual → generic fruit; dropped 低钠.
- **bev_nfc_juice**: removed '赣南脐橙产区直采' origin claim (also wrong for apple); visual '橙色果汁' → juice's own colour; exag '天然维C' false for vitC-fortified apple; dropped 低钠 (1–3 mg).
- **bev_sparkling_zero**: name '苏打气泡水' without 碳酸氢钠 → '气泡水'; '赤藓糖醇代糖' false for cola (aspartame) → generic; exag '碱性苏打水' removed; name '添加膳食纤维' now backed by fiber row (R1 fiber 0.45); peach-only visual → generic; dropped 低钠.
- **bev_tea_drink**: removed '福建高山茶园' origin claim; '茶香清冽' → neutral; dropped 低钠.
- **bev_coffee_drink**: '真牛乳搭配' false for 美式黑咖啡 (水/咖啡/碳酸氢钠); '云南阿拉比卡' origin claim and unbacked '冷萃工艺' removed; exag '黑咖啡燃脂' / '一罐' (PET/利乐 packs) → generic; visual '拉花' (implies milk) → coffee cup.
- **bev_electrolyte**: '清爽柠檬口味' false for 西柚 recipe → '清爽果味'; dropped 低钠 (an electrolyte drink selling sodium).
- **bev_coconut_water**: split: sugared 椰子水饮料 recipe moved to new bev_coconut_water_drink; 100% archetype keeps product_type 果汁; removed '东南亚青椰原产地' origin claim; '不添加糖' now true (only unsweetened recipe); '热带风' generic visual; dropped 低钠.
- **bev_coconut_water_drink**: NEW (split): product_type 果汁饮料 (has 白砂糖, 30% coconut water), PET-bottle packs only, selling without 不添加糖/origin, claims only 无脂肪, exag no longer says '天然输液'.
- **bev_vitamin_drink**: split: 0糖维生素水 moved to new bev_vitamin_water; '0糖款'/'便携罐装'/'一罐' removed (PET packs, sugared recipe); exag '男人加油站' slogan-like → rewritten; silver-blue can (real energy-drink trade dress) → neutral black-green.
- **bev_vitamin_water**: NEW (split): no taurine/caffeine copy, vitc row added (18 mg → 高维生素C + VC function phrase), PET packs only, no caffeine usage note/population.
- **bev_herbal_tea**: '岭南' regional claim removed; '怕上火就喝它' (real-brand slogan) removed; red-can gold-lettering (real-brand trade dress) → neutral green; dropped 低钠.
- **bev_lactic_acid_drink**: split: 非活菌型 recipe moved to new bev_lactic_acid_drink_ambient; removed '每瓶含活性乳酸菌≥100亿' (pack-size dependent) and '小瓶装' (340mL pack); red small-bottle foil-cap visual (real-brand trade dress) → neutral; protein 1.2/1.3→1.5/1.4 (4–4.5% skim milk powder); dropped 低钠.
- **bev_lactic_acid_drink_ambient**: NEW (split): non-live product: no 活菌/冷链 copy, 常温 storage 6 月, claims [] (fat 0.9 fails 无脂肪), attr_tamper '活性乳酸菌饮品'.

## lib_food_b
- **biscuit_oat_choco**: R1 ingredient '黑巧克力' → '黑巧克力（可可液块、白砂糖、可可脂）' so '可可' name/copy is backed; '独立小包装' false for 铁罐/盒装 → removed; visual '透明开窗袋' → pack-neutral.
- **biscuit_wholewheat_soda**: name '海盐全麦苏打饼干' had no 海盐 in any recipe → added recipe (海盐 replaces 食用盐) restricted to that name; visual '袋装' → pack-neutral (1000g 箱).
- **biscuit_sandwich_cream**: removed real-brand slogan '扭一扭舔一舔' and blue-pack + milk-splash sandwich-cookie trade dress; '真果粉添加'/'牛奶夹心' exag only fit one flavour → generic; '双层夹心' → '夹心' (recipes list no separate filling layers).
- **snack_potato_chips**: '充氮…防压碎' / visual '鼓胀铝膜袋' tied to bag (罐装 pack exists) → pack-neutral; odd '配色随口味变化' removed.
- **snack_daily_nuts**: '六种原料' false (recipes have 8 and 7 ingredients) → '多种坚果果干'.
- **snack_seaweed_crisp**: '原味即食海苔' recipe contained 辣椒粉 → removed; '三层夹心' false for 原味 → removed; '精选沿海紫菜' origin wording removed; usage/storage '开罐/罐盖' false for 盒装 → generic; visual '透明塑料罐…夹心' → neutral.
- **snack_beef_jerky**: removed '草原黄牛肉' origin claim and 草原牧场 visual; '独立小包' false for 100g 真空袋.
- **snack_dried_fruit**: '精选产地鲜果' → '精选新鲜果肉'; visual '橙黄色果肉' false for 杨梅 → generic; sodium/salt made consistent (芒果 salt 0.99%→0.2%, sodium 80; 黄桃 salt 0.4→0.1%, sodium 60→100 incl. D-异抗坏血酸钠).
- **snack_freeze_dried_fruit**: visual '粉色…冻干草莓' false for 榴莲/混合 recipes → generic fruit.
- **snack_latiao**: '麻辣' copy false for 甜辣 recipe (no 花椒) → '香辣'; '独立小包' false for 106g bag; exag '大豆蛋白添加' only one recipe → '面筋蛋白' (谷朊粉 in both).
- **snack_konjac**: '麻辣入味' false for 酸辣 recipe (no 花椒) → '香辣'; '素毛肚口感' only fits one name → removed; visual '花椒点缀' → '辣椒点缀'.
- **bakery_mooncake**: removed '广式' regional wording (selling + product_type → 烘烤类月饼); '中秋团圆好礼' season-bound → '团圆送礼好选择'; exag '五种坚果'/'低糖配方' only true for one recipe each → generic. Dropped 低钠; visual '礼盒' → pack-neutral (single-piece pack exists).
- **bakery_toast**: exag '鲜牛乳鸡蛋揉制' false for recipe with 全脂乳粉 (no 牛乳) → '牛奶鸡蛋揉制'.
- **bakery_wholewheat_bread**: name '黑麦全麦切片面包' had no 黑麦 → added recipe with 6% 黑麦粉 restricted to that name; '独立切片' → '切片包装'; visual '袋' → neutral (箱 pack).
- **bakery_swiss_roll**: 抹茶 and 可可 names shared one recipe containing BOTH powders → split into separate recipes; '瑞士卷' → '蛋糕卷' (place-style wording); exag '动物奶油夹心' false for 植脂奶油-only recipes → '奶油夹心'.
- **cereal_instant_oat**: removed '澳洲燕麦' origin claim; dropped 低钠 (5 mg); visual '大罐' → pack-neutral.
- **cereal_granola**: '果粒坚果满满' false for 酸奶果粒/奇亚籽 recipe (no nuts) → '谷物果干满满'; exag '奇亚籽+菊粉' only one recipe → generic; visual '草莓、坚果' → '果干'.
- **cereal_black_sesame_paste**: dropped 低钠; visual '袋' → pack-neutral (罐装).
- **cereal_lotus_root_powder**: removed '西湖传统工艺' origin claim; '坚果果干料足' false for 纯藕粉 recipe → removed; dropped 低钠.
- **snack_protein_bar**: '一支补充16g蛋白质' (numeric; false for grain-bar recipe) and '巧克力脆皮' (only whey bar) removed; visual '大号蛋白质克数' removed; R1 维生素E 2.0%→0.02% (antioxidant level); R0 sugar 4.5→8.5 (16% 代可可脂巧克力 contains sugar; 低糖 then fails engine check).
- **snack_chocolate**: '纯可可脂' false for 榛仁夹心 (植物油) → removed; '西非可可豆' origin removed; '独立小片' false for 排块/碗装; exag '85%黑巧'/'黑巧克力'/'高纯度' only fit one recipe → generic; dropped 低钠; visual '排块纸盒' → pack-neutral.
- **bee_honey**: '源自山区蜂场' place claim → '蜂场直供'; visual '槐花' false for 百花/枣花, '玻璃瓶' false for 挤压瓶/条装 → neutral; dropped 低钠.
- **candy_hard**: '清凉提神' false for 水果味 (no 薄荷); '果香浓郁' false for 薄荷无糖; '小铁盒' false for 袋装; exag '蜂蜜柠檬'/'无糖' only fit one recipe → generic; visual '马口铁盒…水果插画' → neutral; dropped 低钠; '颗颗独立' replaced to avoid pack claims.
- **candy_gummy**: exag '胶原蛋白软糖'/'补维C' only fit collagen recipe → generic; visual '粉紫色袋装…葡萄' → neutral (罐装 pack, 石榴 recipe); dropped 低钠.
- **candy_pressed_vc**: '香橙口味' (no orange ingredient), '随身小瓶' (铝塑板 pack), '一片含维C约11mg' (numeric, pack-dependent) removed; 钙片 name now backed by a calcium row (row shown only for the calcium recipe); exag '钙片' removed from generic line; orange 'VC' visual false for 钙片 → neutral.
- **candy_nougat**: visual '粉色莓果' false for 花生 recipe → removed.
- **snack_freeze_dried_fruit**: dropped 低钠 (10–20 mg, sodium-free product).
- **kids_yogurt_melts**: '酸奶溶豆' shared the strawberry recipe (草莓果粉+甜菜红) → new plain recipe for name 0; protein 10/12→12–13.5 (18–30% 乳粉 + 8% 鸡蛋清粉).
- **kids_rice_cracker**: '原味宝宝米饼' shared the carrot recipe (胡萝卜粉+β-胡萝卜素) → new plain rice recipe for that name; '独立小包' false for 120g bag, '卡通造型' unbacked → removed; exag '真蔬菜添加' → generic; visual '胡萝卜兔子' → generic.
- **kids_jelly**: product_type '果冻（含果肉型）' false for the no-pulp recipe → '果冻'; name '乳酸菌果冻' had no 菌 ingredient → '酸奶味果冻'; '可吸果冻' implied a pack (杯装 exists) → '果汁果冻'; '真果肉看得见' only fit one recipe; exag '乳酸菌果冻' → generic; visual '杯装组合…封膜' → neutral.
- **kids_meat_floss**: '原味猪肉松' shared the 海苔 recipe → new plain pork recipe (no 海苔/芝麻); '海苔芝麻香气足' only fit one name → removed; exag '鳕鱼添加' → generic; visual '海苔碎' removed.
- **kids_teething_biscuit**: '可爱动物造型' only fits name 1 → replaced; '独立小包' false for 罐装; visual '动物形饼干' → generic.
