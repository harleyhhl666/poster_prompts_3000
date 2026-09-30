# Schemas for lib_supplement.py / lib_welfare.py / lib_event.py

All text Simplified Chinese, China-market realistic, ALL brands/companies/organisations fictional (no real brand, no real hospital/NGO names;
government-type organisers must be generic fictional ones like “江宁区青云街道社区卫生服务中心”, “临川市市场监督管理局（示例）” is NOT wanted —
just use fictional place names such as 临川市、青禾区、望江县, never real cities' real agencies). Real hotline 12315 (market regulation complaints) and 120 (emergency) may be used.

## Verified facts you MAY state as facts (sources checked)
- 《中国居民膳食指南（2022）》准则五：成年人每天摄入食盐不超过5g，烹调油25～30g；添加糖每天不超过50g，最好控制在25g以下；反式脂肪酸每天不超过2g；不喝或少喝含糖饮料；儿童青少年、孕妇、乳母以及慢性病患者不应饮酒；成年人如饮酒，一天饮用的酒精量不超过15g。
- 准则一：平均每天摄入12种以上食物，每周25种以上；每天谷类200～300g，其中全谷物和杂豆类50～150g；薯类50～100g。
- 其他（指南核心推荐）：餐餐有蔬菜，每天300～500g，深色蔬菜占1/2；天天吃水果200～350g，果汁不能代替鲜果；每天奶类300mL以上（原文“300ml以上”）；每周中等强度身体活动150分钟以上，主动身体活动最好每天6000步。
- GB 7718-2025（2027-03-16实施）：八类致敏物质用作配料须强制标示：含有麸质的谷物及其制品、甲壳纲类动物及其制品、鱼类及其制品、蛋类及其制品、花生及其制品、大豆及其制品、乳及乳制品（包括乳糖）、坚果及其果仁类制品；预包装食品须同时标示生产日期和保质期到期日；日期按年、月、日顺序标示；配料按加入量递减顺序排列，加入量不超过2%的可不按递减顺序；共线生产可能带入致敏物质时鼓励标示“可能含有……”。
- GB 28050-2011：营养成分表强制标示能量和4种核心营养素（蛋白质、脂肪、碳水化合物、钠）及NRV%；NRV：能量8400kJ、蛋白质60g、脂肪≤60g、碳水化合物300g、钠2000mg、钙800mg、膳食纤维25g；“无糖”≤0.5g/100g(mL)；“低糖”≤5g/100g(mL)；“低脂”≤3g/100g固体、≤1.5g/100mL液体；“高蛋白”≥12g/100g或≥6g/100mL；“低钠”≤120mg/100g(mL)。
- 保健食品：《保健食品标注警示用语指南》（2020-01-01起实施）警示用语“保健食品不是药物，不能代替药物治疗疾病。”；保质期以“保质期至XXXX年XX月XX日”方式标注；认准保健食品标志（俗称“小蓝帽”）及批准文号；遇到夸大功效、宣传疾病治疗功能，可拨打12315投诉举报。
- 《允许保健食品声称的保健功能目录 非营养素补充剂（2023年版）》24项：有助于增强免疫力；有助于抗氧化；辅助改善记忆；缓解视觉疲劳；清咽润喉；有助于改善睡眠；缓解体力疲劳；耐缺氧；有助于控制体内脂肪；有助于改善骨密度；改善缺铁性贫血；有助于改善痤疮；有助于改善黄褐斑；有助于改善皮肤水份状况；有助于调节肠道菌群；有助于消化；有助于润肠通便；辅助保护胃粘膜；有助于维持血脂（胆固醇/甘油三酯）健康水平；有助于维持血糖健康水平；有助于维持血压健康水平；对化学性肝损伤有辅助保护作用；对电离辐射危害有辅助保护作用；有助于排铅。超出目录的功能宣称均属违规；宣传“根治”高血压、糖尿病等属违法虚假宣传。
- General, uncontroversial food-safety advice (生熟分开、烧熟煮透、冷藏2—8℃/冷冻-18℃以下、勤洗手、不吃来源不明食品、不采食野生蘑菇、隔夜菜冷藏并彻底加热 等) may be used as ordinary advice without numbers beyond these.
Any OTHER quantitative health/regulatory claim must NOT be written as fact. If you need one, phrase it as general advice without numbers.

---------------------------------------------------------------------------------------------------
## lib_supplement.py  →  `SUPPLEMENTS = [ {...}, ... ]`  (target ≥ 32 entries, varied)
```python
{
 "id": "vc_chewable",
 "sub_category": "维生素矿物质",   # 维生素矿物质 / 钙与骨骼 / 鱼油与脂类 / 益生菌与肠道 / 蛋白粉与运动营养 / 胶原蛋白与美容 / 叶黄素与护眼 / 膳食纤维 / 辅酶Q10 / 植物提取物 / 睡眠 / 中老年营养 / 儿童营养 / 女性营养 / 免疫
 "reg_type": "保健食品-备案",     # "保健食品-注册" | "保健食品-备案" | "普通食品" | "运动营养食品" | "特殊医学用途配方食品" (use last rarely; if used, standard GB 29922-2013 is NOT verified -> no standard)
 # 保健食品-备案 = 营养素补充剂 type (vitamins/minerals) ; 保健食品-注册 = function claims from the 24-item list ;
 # 普通食品 = e.g. 益生菌固体饮料, 胶原蛋白肽饮品, 叶黄素酯压片糖果, 酵素饮品: these may NOT claim health functions (great anomaly source)
 "names": ["维生素C咀嚼片（甜橙味）", "维生素C咀嚼片（草莓味）"],   # no brand; engine prepends fictional brand + "牌" for 保健食品 (e.g. “禾安康牌维生素C咀嚼片”)
 "dosage_form": "咀嚼片",
 "spec": ["1.2g/片×60片", "1.2g/片×100片"],
 "price": [59.0, 168.0],
 "raw_materials": "维生素C、甘露糖醇、微晶纤维素、甜橙粉、硬脂酸镁、二氧化硅",   # 原料/配料 as printed, realistic order
 "hero_first_tamper": "甜橙粉、维生素C、甘露糖醇、微晶纤维素、硬脂酸镁、二氧化硅",  # reordered version that makes the product look 'more natural' (ingredient-order tamper); must contain exactly the same items
 "allergens": [],                     # subset of 麸质, 甲壳, 鱼, 蛋, 花生, 大豆, 乳, 坚果 actually present (e.g. 乳清蛋白 -> 乳; 大豆分离蛋白 -> 大豆; 鱼油软胶囊 with 明胶 from fish? use 鱼 only if fish-derived non-exempt ingredient; refined fish oil is exempt -> []
 "components": "每片含：维生素C 100mg",   # 标志性成分及含量 / 营养成分 as printed
 "health_function": "补充维生素C",      # 保健食品-备案: "补充XX"; 保健食品-注册: EXACT item from the 24-list; 普通食品: None
 "suitable": "需要补充维生素C的成人",
 "unsuitable": "少年儿童、孕妇、乳母",    # may be None for 普通食品
 "usage": "每日1次，每次1片，嚼服",
 "cautions": ["本品不能代替药物", "不宜超过推荐量或与同类营养素补充剂同时食用", "适宜人群外的人群不推荐食用本产品"],
 "shelf": [24, "月"],                  # value, unit (月)
 "shelf_tamper": [36, "月"],
 "storage": "密封，置阴凉干燥处",
 "normal_copy": ["每片100mg维生素C", "甜橙口味，方便嚼服"],               # compliant selling copy
 "exag_subtle": ["每天一片，换季少生病", "有效提升抵抗力"],              # slightly over-the-line (dataset-designed anomaly)
 "exag_strong": ["7天增强免疫力，远离感冒病毒", "替代药物预防流感"],       # clearly illegal-style medical/absolute claims, realistic ad talk
 "population_tamper": "儿童、孕妇、老人全家适用",                        # text that illegally widens suitable population
 "attr_tamper": None,                 # e.g. for 普通食品: "保健食品 增强免疫" style mislabel text; for 保健食品: "药字号品质" etc.
 "visual": "橙色白色塑料瓶，瓶身有鲜橙切片插画",
}
```

---------------------------------------------------------------------------------------------------
## lib_welfare.py  →  `WELFARE = [ {...}, ... ]`  (target ≥ 36 entries)
公益海报 (non-commercial public-interest posters). Each entry is a THEME with enough real content for a high-density poster.
```python
{
 "id": "salt_reduction",
 "sub_category": "控盐宣传",    # 食品安全宣传/营养健康宣传/反食品浪费/控盐宣传/控糖宣传/控油宣传/食品过敏原宣传/老年人保健品防骗/儿童食品消费科普/防范虚假保健品宣传/食品标签阅读科普/临期食品科普/食源性疾病预防/校园食品安全/社区健康教育/特殊人群饮食提示/野生菌中毒预防/节日饮食安全/外卖食品安全/饮水安全 … extend
 "titles": ["减盐 从每一餐开始", "少一勺盐 多一分健康"],    # ≥2 alternatives
 "subtitles": ["成年人每天食盐不超过5克"],
 "organizer_types": ["社区卫生服务中心", "街道办事处", "疾病预防控制中心"],  # generic kinds; engine invents fictional names
 "sections": [                     # 3–5 content blocks, each 3–6 items; concrete, poster-ready sentences (≤ 30 chars each)
    {"heading": "为什么要减盐", "items": ["...", "..."]},
    {"heading": "减盐小妙招", "items": ["...", "..."]},
    {"heading": "看懂标签里的“钠”", "items": ["...", "..."]}
 ],
 "numbers": [                     # key facts in the poster that can be TAMPERED (fact tamper). value exactly as appears in some item/subtitle text
    {"text": "成年人每天食盐不超过5克", "tampered": "成年人每天食盐不超过10克", "source": "中国居民膳食指南（2022）"}
 ],
 "key_warning": "高血压患者请遵医嘱控制钠摄入",   # the single most important caution line (can be deleted in tamper)
 "misinfo_subtle": "低钠盐人人适用，可以放心多放",       # mildly wrong advice inserted naturally (dataset-designed anomaly)
 "misinfo_strong": "每天吃够两勺蒜泥即可抵消多吃的盐",   # clearly wrong, realistic rumour-style advice
 "cta": "扫码参加“21天减盐打卡”",
 "has_event": True,               # whether poster naturally carries an activity date/place (engine generates)
 "event_kinds": ["社区健康讲座", "免费测血压"],  # if has_event
 "visual_styles": ["社区公益风", "医疗科普风", "政务宣传栏风"],
 "visual_motif": "白色盐勺、蔬菜、心形血压计图标",
}
```

---------------------------------------------------------------------------------------------------
## lib_event.py  →  `EVENTS = [ {...}, ... ]`  (target ≥ 30 entries)
活动宣传 posters (commercial + public events). Engine adds fictional organiser, venue, dates, times, fees, quotas.
```python
{
 "id": "yogurt_tasting",
 "sub_category": "试吃活动",   # 商场促销活动/试吃活动/新品品鉴会/健康讲座/营养讲座/社区宣传活动/食品安全周/校园健康周/公益宣传日/产品发布会/保健品说明会/展览展销会/品牌快闪/节日市集/公益义卖/免费检测活动/健康咨询/烘焙课堂/亲子厨房/农产品展销/美食节/开业庆典/会员日 … extend
 "commercial": True,
 "title_patterns": ["{brand}新品酸奶免费试吃", "{brand}鲜酪乳 限时试吃周"],   # {brand} placeholder allowed ONLY here; engine fills it
 "product_hint": "风味发酵乳",   # or None
 "agenda": [ ["10:00—10:30", "新品介绍"], ["10:30—12:00", "现场试吃"] ],   # 3–6 slots; engine may shift times consistently
 "perks": ["现场试吃即送品鉴小样1杯", "扫码入会领5元无门槛券"],
 "rules": ["每人限领1份", "赠品数量有限，送完即止"],
 "hidden_condition": "需购买任意2件商品后方可领取品鉴小样",   # hidden paid condition for tamper ("免费"但隐藏付费条件)
 "quota": 200,                   # participant/gift quota (engine may contradict in tamper)
 "fee": "免费",                   # "免费" | "¥39/人" etc
 "venue_types": ["商场一层中庭", "超市入口促销区"],
 "duration_days": [2, 7],        # min/max length
 "daily_hours": ["10:00—21:00", "10:00—20:00"],
 "speaker_roles": None,           # e.g. ["注册营养师", "社区医生"] for lectures
 "health_related": False,         # if True, include a proper disclaimer line (e.g. 讲座不推销任何产品 / 保健食品不是药物…)
 "disclaimer": None,              # the normal compliant disclaimer line (deleted in warning_deletion tamper)
 "exag_line": None,               # for 保健品说明会/健康讲座: a strong illegal promise, e.g. "现场购买即可停药" (dataset-designed anomaly)
 "visual_styles": ["商场促销风", "年轻潮流风"],
 "visual_motif": "奶白色背景、酸奶杯与蓝莓",
}
```
