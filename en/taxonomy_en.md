# 英文（欧洲 + 北美）富文字图像提示词 —— Taxonomy（英文部分 v1.0）

> 版本 v1.0（2026-11-13）｜与中文 3000 条同一套设计（三联配对、逐字文本、规格级篡改真值），面向欧洲（EU/EEA、英国、瑞士）与北美（美国、加拿大）英文场景。
> 本文件在全量生成之前定稿；配额、地区分配、篡改权重写在这里并与 `en/src/generate_en.py` 中的常量一致，生成后不回调。

## 0. 与中文部分保持一致的原则

1. 每条 prompt 写明载体、画幅、分区版式，图中每段文字都逐字写在「」内（括号本身不画），不让模型自由发挥。
2. 三联：`clean / subtle / strong`，同组产品、品牌、载体、版式、配色一致，只改关键文字；异常不做视觉标记。
3. 品牌、公司、零售商、主办方全部虚构，并用 250+ 条真实品牌/零售商黑名单过滤（`lib_names_en.REAL_BRAND_BLACKLIST`，名字片段双向子串检查）。
4. 法规口径分级：只有逐条读过原文的规则才写成"规定"（§6.1），其余一律标 **dataset-designed anomaly**。
5. 篡改真值写进 `tamper_details`，每条都能在 prompt 文字里定位。

## 1. 一级类别与冻结配额

1000 不能被 3 整除。按用户选择，用 **334 组 × 3 = 1002 条**，保持三联完整。比例与中文部分（31/24/16/15/14%）一致：

| super_category | 中文对应 | 组 | 条 |
|---|---|---:|---:|
| Food label | 食品标签 | 104 | 312 |
| Commercial ad | 商业广告 | 80 | 240 |
| Supplement | 保健品说明 | 53 | 159 |
| Event | 活动宣传 | 50 | 150 |
| Public-service poster | 公益海报 | 47 | 141 |
| **合计** | | **334** | **1002** |

ID 接在中文后面：`P003001`–`P004002`，`G1001`–`G1334`，新增 `lang="en"`、`country`、`region` 三个字段。

## 2. 地区分配（冻结）

"欧美" = 欧洲（EU/EEA、英国、瑞士）+ 北美（美国、加拿大），33 个国家，全部英文文字。英文在非英语国家出现必须有理由：引擎为每个非英语国家的场景加一句语境（国际超市、机场/车站、应用英文版、外籍社区、大学校园、国际学校等），并按载体筛选语境（广告用零售类，活动/公益用社区类）。

| 类别 | 分配 | 说明 |
|---|---|---|
| Food label | UK 34 / US 34 / IE 24 / MT 12 | 只放在英文标签合法的市场（EU 1169/2011 Art 15 要求消费者易懂的语言），产地从欧洲/北美各国中选，进口品附进口商/经销商 |
| Supplement | US 27 / UK 14 / IE 8 / MT 4 | 美国 Supplement Facts vs 欧盟/英国 food supplement 两套监管结构 |
| Commercial ad | UK 16 / IE 8 / US 20 / 欧洲大陆 36 | 加拿大不做食品广告（加拿大标签需英法双语，且其 DV 未核实）；欧洲大陆国家按"最少使用"轮换 |
| Event | UK 9 / IE 5 / US 10 / CA 6 / 欧洲大陆 20 | |
| Public-service poster | UK 9 / IE 5 / US 10 / CA 5 / 欧洲大陆 18 | 事实按地区取用（°F/FDA/USDA 只用于美加，NHS 只用于英爱，WHO/CDC 通用） |

货币按 2026–27 实际在用：EUR（含 HR、BG 自 2026-01-01）、GBP、USD、CAD、CHF、SEK、DKK、NOK、ISK、PLN、CZK、HUF、RON。价格由欧元区间按近似汇率换算并取零售尾数（.99/.49/.95…）；活动票价取整或 .50。

## 3. 二级类别

- **Food label（14 类，64 个原型）**：Dairy & alternatives、Beverages、Breakfast cereals、Baby & kids、Snacks、Confectionery、Bakery & biscuits、Spreads & sauces、Seasonal、Ready meals & frozen、Meat, fish & deli、Canned & jarred、Pasta, rice & grains、Meal replacement & sports。载体 7 种：背面平铺、正背面并列、瓶身/罐身环绕标签（两视图）、罐头、纸盒侧面、冷柜冷冻袋、手持翻面实拍。
- **Commercial ad（9 种载体）**：货架上方促销海报、网店移动端长图、季节活动海报、门口 A 字立牌、货架价签 + 摇摆牌、新品上市海报、周刊 DM 单页、橱窗海报、外卖 App 秒杀页。促销机制按地区：Was/Now、Save X%、Any N for X、BOGOF、3 for 2、2nd item half price、Member price、Flash deal（限量）、Digital coupon（美）。
- **Supplement（16 子类，32 个产品）**：维生素矿物质、骨骼、鱼油、益生菌、运动、胶原、护眼、膳食纤维、CoQ10、植物提取物、睡眠、50+、儿童、女性、免疫、孕期。载体 6 种：瓶身环绕标签、纸盒正背面、说明书、网上药房详情页、药店货架海报、直播带货商品卡。
- **Event（39 个原型）**：试吃、新品发布、健康讲座、营养工作坊、烹饪课、儿童厨房、农夫市集、圣诞市集、美食节、慈善义卖、食物银行募集、免费体检、保健品说明会、开业、会员日、店庆、咖啡杯测、奶酪面包品鉴、巧克力工作坊、校园健康周、职场健康日等。
- **Public-service poster（34 个主题）**：控盐、控糖、过敏原（EU 14 类 / US 9 类）、日期标签、食物浪费、手卫生、冰箱与剩菜、节日食品安全、野生蘑菇、老年人保健品防骗、营养标签阅读、校园餐、网购食品、食品欺诈、烧烤安全、生乳奶酪风险、孕期饮食、健康老龄化、婴儿喂养、食物银行、饮水等。

## 4. 文本密度（英文口径，冻结）

英文每个信息单位的字符数约为中文的 2–3 倍，所以阈值按「」内逐字字符数重新设定：Low < 200，Medium 200–499，High 500–1199，Very High ≥ 1200。目标：Very High ≥ 50%，Medium + Low ≤ 10%（只报告，不为凑比例调内容）。

## 5. 字段库（与中文部分一一对应）

| 字段 | EU/UK/MT 标签 | US 标签 |
|---|---|---|
| 品名 + 法定名称 | brand + product name；name of the food（Art 17） | statement of identity |
| 配料 | `Ingredients:` 按加入量递减；过敏原在配料内用 CAPITALS 强调；品名/强调配料带 QUID % | `INGREDIENTS:` 全大写；美式拼写 |
| 过敏原 | `Allergy advice: … see ingredients in CAPITALS.` + 可选 `May contain …` | `CONTAINS: MILK, WHEAT.`（9 类）+ 可选 `MAY CONTAIN …` |
| 营养表 | `Nutrition / Per 100g / Per {portion} / %RI*`，能量 kJ/kcal，fat、saturates、carbohydrate、sugars、(fibre)、protein、salt，可选维生素矿物质 %NRV，脚注 RI 8400kJ/2000kcal | Nutrition Facts：servings per container、serving size、Calories、%DV（含 added sugars、Vitamin D、Calcium、Iron、Potassium），FDA 标准脚注 |
| 营养声称 / 健康声称 | 1924/2006 附录条件自动校验；健康声称只用 432/2012 原文 | 按每份（RACC 用 serving size 近似）映射为 Low fat / Fat free / Sugar free / Low sodium / Good/Excellent source of … |
| 日期三件套 + 批号 | `Production date / Best before 或 Use by / Shelf life (unopened) / Lot` + 包装上的 inkjet 喷码（BB + Lot） | `PROD / BEST BY 或 USE BY / Shelf life / LOT` + 喷码 |
| 净含量 | `500g ℮` 或 `6 x 25g` | `NET WT 17.6 OZ (1 LB 1.6 OZ) 500g` |
| 生产者/进口商 | Produced in … by …；Imported and distributed by …；客服地址电话 | Manufactured by / Imported by；客服 |
| 条码 | EAN-13（GS1 前缀按国家，校验位正确，号码虚构） | UPC-A（校验位正确） |

日期约定（dataset convention，同中文部分）：到期日 = 生产日期 + 保质期 − 1 天。批号 4 种格式（`L27037B` 年+年内日序、`L 060227 B`、`LOT 270206-07`、`L20270206B`），日期段与生产日期一致；美国标签只用 `LOT YYMMDD-NN`。展示时间窗：2026-10-01 至 2027-04-30，节日窗口由程序计算（2027 复活节 3 月 28 日，Shrove Tuesday = 复活节 − 47 天，美国感恩节 = 11 月第 4 个星期四，等等）。

## 6. 法规依据与 dataset-designed anomaly 边界

### 6.1 已读原文核实的规则（2026-11-13）

| 规则 | 来源 | 用于 |
|---|---|---|
| 配料以 "ingredients" 为标题，按制造时加入量递减排列；占成品 < 2% 的配料可在其余配料之后不按顺序排列 | Reg (EU) 1169/2011 Art 18(1)、Annex VII Part A 第 6 点 | ingredient_order_tamper（只移动 hero 配料到用量更大的配料之前） |
| 品名中出现或被强调的配料须标注数量（QUID） | 1169/2011 Art 22 | 配料 % 与正面 "Now with X%" 冲突 |
| 14 类过敏原（Annex II）须在配料表中以字体/样式/底色与其他配料区分；含小麦葡萄糖浆、小麦麦芽糊精、大麦葡萄糖浆、全精炼大豆油、乳糖醇等豁免 | 1169/2011 Art 21(1)(b) + Annex II | allergen_deletion（EU） |
| 强制营养声明：energy、fat、saturates、carbohydrate、sugars、protein、salt；顺序与单位按 Annex XV；salt = sodium × 2.5；能量换算系数（碳水/蛋白 17 kJ、脂肪 37 kJ、纤维 8 kJ…） | 1169/2011 Art 30、Annex I 第 11 点、Annex XIV、Annex XV | nutrition_value_tamper（能量与宏量营养素不自洽） |
| RI：8400 kJ/2000 kcal、fat 70 g、saturates 20 g、carbohydrate 260 g、sugars 90 g、protein 50 g、salt 6 g；维生素矿物质 NRV（如 Vit D 5 µg、Ca 800 mg、Fe 14 mg）；"significant amount" = 每 100 g 15% NRV（饮料每 100 ml 7.5%） | 1169/2011 Annex XIII Part A/B | %RI / %NRV 校验；"Source of …" 声称条件 |
| 日期：'Best before …'（含日）/'Best before end …'；微生物易腐食品用 'Use by …' | 1169/2011 Art 24、Annex X | 日期字段 |
| 营养声称条件：low fat ≤ 3 g/100 g（液体 1.5 g/100 ml）；fat-free ≤ 0.5 g；low sugars ≤ 5 g（液体 2.5 g）；sugars-free ≤ 0.5 g；no added sugars；low salt ≤ 0.12 g sodium；source of fibre ≥ 3 g/100 g 或 1.5 g/100 kcal；high fibre ≥ 6 g 或 3 g/100 kcal；source of protein ≥ 12% 能量；high protein ≥ 20% 能量；low energy ≤ 40 kcal/100 g（液体 20） | Reg (EC) 1924/2006 Annex | claim_nutrition_conflict；clean 声称由程序按阈值过滤 |
| 健康声称只能用授权原文（215 条已抽取到 `en/refs/eu432_claims.json`）且满足使用条件 | Reg (EU) 432/2012 Annex | 食品/保健品 clean 声称；function_upgrade |
| 食品补充剂标签须有：每日推荐量、"不超过推荐日剂量"警示、"不能替代多样化膳食"、"放在幼儿接触不到的地方"；不得宣称预防、治疗或治愈疾病 | Directive 2002/46/EC Art 6(2)(3) | warning_deletion、efficacy_exaggeration（EU 保健品） |
| 批号前加字母 "L"（与其他标示可区分时除外） | Directive 2011/91/EU Art 3 | 批号格式 |
| US DV：fat 78 g、sat 20 g、cholesterol 300 mg、sodium 2300 mg、total carb 275 g、fiber 28 g、added sugars 50 g、protein 50 g、Vit D 20 mcg、Ca 1300 mg、Fe 18 mg、K 4700 mg（及其他维生素矿物质 RDI） | 21 CFR 101.9(c)(8)(iv)、(c)(9) | %DV 校验 |
| US 取整：热量 ≤ 50 取 5 的倍数、> 50 取 10 的倍数、< 5 记 0；脂肪 < 5 g 取 0.5 g、≥ 5 g 取 1 g、< 0.5 g 记 0；钠 5–140 mg 取 5 mg、> 140 取 10 mg；碳水/蛋白取整克；份数 2–5 取 0.5 并用 "about" | 21 CFR 101.9(b)(8)、(c)(1)(2)(4)(6) | US 营养表 |
| US 脚注原文 "The % Daily Value tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice." | 21 CFR 101.9(d)(9) | US 营养表 |
| 声称：fat free < 0.5 g、low fat ≤ 3 g（每 RACC）；sugar free < 0.5 g；low sodium ≤ 140 mg；good source 10–19% DV；high/excellent source ≥ 20% DV | 21 CFR 101.62、101.60、101.61、101.54 | US 声称映射 |
| 9 类主要过敏原：milk, eggs, fish, crustacean shellfish, tree nuts, peanuts, wheat, soybeans, sesame | FDA "Food Allergies" 页面（FALCPA + FASTER Act） | allergen_deletion（US） |
| Supplement Facts 版式；结构/功能声称须带 DSHEA 免责声明原文；含铁固体剂型须带铁剂过量警示原文 | 21 CFR 101.36、101.93(c)、101.17(e) | warning_deletion、regulatory_status_tamper（US 保健品） |
| FDA 不在上市前批准膳食补充剂 | FDA "Questions and Answers on Dietary Supplements" | regulatory_status_tamper（"FDA approved"） |

公益海报的定量事实只用 `en/refs/facts_whitelist.md` 中 27 条已核实事实（WHO 盐 < 5 g/天、NHS 盐 ≤ 6 g、NHS 游离糖 ≤ 30 g、WHO 游离糖 < 10% 能量、CDC 洗手 20 秒、FDA 冰箱 40°F、FSA 冰箱 0–5°C、USDA 危险温度带与 2 小时规则、家禽 165°F、112/999/911/NHS 111、Poison Help 1-800-222-1222 等），每条注明来源与适用地区。

### 6.2 dataset-designed（数据集约定，不作为法律结论）

- 日期三件套 + 喷码：EU 不强制标生产日期，美国联邦层面除婴儿配方外不强制日期（USDA FSIS）。数据集为了与中文部分可比，统一印"生产日期 + 到期日 + 保质期 + 批号"，异常按信息一致性定义。
- EU 四舍五入采用欧盟委员会 2012 年容差指南的通行口径（未逐字核对）；US 维生素矿物质取整（Vit D 0.1 mcg、Ca/K 10 mg、Fe 0.1 mg）采用 FDA 指南通行做法（未逐字核对）。QA 校验留有取整容差。
- US 营养声称用 serving size 近似 RACC；US 不做蛋白质声称（需 PDCAAS）。
- 喷码与印刷信息不一致、两处地址门牌号不同、产地徽标与生产商地址不符、"Organic" 等无依据属性、"Licensed medicine" 冒充、折扣算错、横幅与小字期限不符、星期与日期不符、名额前后不一致、流程时间重叠、隐藏付费条件、来源被改、电话被改——全部为 dataset-designed anomaly。
- 动物源性食品的 EU 识别标记（椭圆章）：2024 年欧盟修改了缩写规则（Reg 2024/1141），各国写法未逐一核实，**不使用**，因此删去中文部分的"执行标准号篡改"，对应权重并入批号与生产者信息两类。

## 7. 篡改类型库（29 种）与冻结权重

### 7.1 五个重点类型（与中文部分相同）

| 类型 | subtle | strong |
|---|---|---|
| efficacy_exaggeration | 一条卖点改为轻度夸大（"Supports strong bones for life"） | 大字疾病/绝对化宣称（"Clinically proven to prevent osteoporosis"、"Lowers blood pressure without medication"） |
| allergen_deletion | EU：一个含过敏原配料失去 CAPITALS 强调；US：CONTAINS 中删掉一项；保健品：删过敏原声明 | 全部强调/CONTAINS 删除，并加冲突的 "Dairy free / Gluten free / Nut free" 徽标 |
| production_date_tamper | 生产日期移动 3–10 天（到期日与喷码同步），批号仍对应原日期 | 改标：印刷生产日期、到期日、批号整体后移（夹在展示日期之前），喷码仍为原值；广告中无喷码时改为生产日期晚于活动开始日 |
| shelf_life_tamper | 保质期数值改长，到期日未变 | 保质期与到期日一起延长；冷藏/冷冻品同时改成 "Store in a cool, dry place." |
| ingredient_order_tamper | 一个 hero 配料前移 1–2 位（若两者都带 QUID % 则单图可见） | 全部 hero 配料提到最前、真实首位后移，正面加 "Now with X% …" 与配料表 QUID 冲突（美国保健品配料只列 Other ingredients，不适用） |

### 7.2 扩展类型

nutrition_value_tamper、claim_nutrition_conflict、quantity_tamper（含 oz 与 g 换算不符）、batch_number_tamper（喷码与印刷批号差一位 / 批号日期段与生产日期不符）、manufacturer_info_tamper（客服地址门牌号与生产商/进口商地址不同 / 产地徽标与地址不符并删进口商）、storage_condition_tamper、product_attribute_tamper、target_population_tamper、warning_deletion（开封后保存期限、保健品强制警示、DSHEA 免责声明、讲座免责声明、公益重点提示）、price_tamper、promotion_date_tamper、promotion_rule_tamper、hidden_fee_condition、quota_contradiction、regulatory_status_tamper（"FDA approved"、"Licensed medicine"）、function_upgrade（授权声称被改写为"Powerfully boosts…"）、unsubstantiated_claim、health_fact_tamper、misinformation_insertion、event_date_tamper、venue_tamper、agenda_time_conflict、contact_info_tamper（热线差一位 / 急救号码写错）、source_attribution_tamper。

### 7.3 主篡改目标权重（缺口平衡器使用）

| 类别 | 权重 |
|---|---|
| Food label | ingredient_order 22, allergen 24, production_date 18, shelf_life 18, efficacy 9, nutrition_value 8, claim_conflict 8, batch 5, manufacturer 5, quantity 3, storage 2, attribute 2, warning 2, population 1 |
| Commercial ad | price 18, promotion_date 15, efficacy 14, allergen 12, ingredient_order 12, production_date 9, shelf_life 9, claim_conflict 7, quantity 5, hidden_fee 4, quota 3, promotion_rule 3, nutrition_value 3, attribute 2 |
| Supplement | efficacy 22, warning 14, allergen 12, ingredient_order 12, shelf_life 12, population 10, production_date 9, regulatory_status 8, attribute 5, function_upgrade 5, unsubstantiated 2, nutrition_value 2, manufacturer 2 |
| Event | event_date 20, hidden_fee 18, venue 12, quota 12, promotion_rule 10, warning 10, efficacy 8, agenda 6, price 6 |
| Public-service poster | health_fact 25, misinformation 25, warning 15, event_date 12, contact 12, source 6, quota 5 |

### 7.4 每组计划（同中文部分）

主类型由权重 + 缺口平衡器决定；subtle 含主类型，40% 概率再加 1 个隐蔽类型；strong 包含 subtle 的全部类型并补到 2–3 个，且比 subtle 至少多 1 个。引擎先探测适用性，不适用的类型不会写进元数据。每个版本都从头重建（同一 md5 种子），不共享被修改的状态。

## 8. 元数据 schema

`id, group_id, variant, lang, super_category, sub_category, country, region, scene_type, product_type, visual_style, layout, aspect_ratio, text_density, required_fields[], tamper_types[], tampered_fields[], tamper_details[], difficulty, single_image_detectable, carrier, realism, brand_or_organizer, product_or_title, source_archetype, prompt`

## 9. 已知局限（预先声明）

1. 营养数值是品类典型值 ± 5% 抖动后的虚构值，不是检测值。
2. 英文 Very High 密度的小字（配料、营养表、规则）在生图时仍可能漏行，出图后应 OCR 比对「」文本，失败样本重生成，不修改元数据去迁就图像。
3. 欧洲大陆的英文场景依赖"国际/游客/外籍社区"语境，数量上是真实市场的少数情况，这是"全英文"要求下的设计取舍。
4. 加拿大只出现在活动与公益海报中。
5. EAN/UPC、电话、邮编只模拟格式；美国、加拿大电话用 555-01xx 虚构段，英国用 Ofcom 影视专用号段。
