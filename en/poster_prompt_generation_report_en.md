# 英文部分生成报告（自动生成：`python en/src/make_report_en.py`）

## 1. 总量

共 **1002** 条提示词，**334** 个三联组（clean/subtle/strong 各 334 条），ID `P003001`–`P004002`。

## 2. 一级类别

| super_category | 中文对应 | 组 | 条 |
|---|---:|---:|---:|
| Food label | 食品标签 | 104 | 312 |
| Commercial ad | 商业广告 | 80 | 240 |
| Supplement | 保健品说明 | 53 | 159 |
| Event | 活动宣传 | 50 | 150 |
| Public-service poster | 公益海报 | 47 | 141 |
| 合计 |  | 334 | 1002 |

## 3. 二级类别

**Food label**（14 种）：Bakery & biscuits 11、Dairy & alternatives 10、Beverages 10、Ready meals & frozen 9、Meat, fish & deli 8、Spreads & sauces 8、Snacks 8、Confectionery 7、Canned & jarred 7、Pasta, rice & grains 7、Breakfast cereals 6、Meal replacement & sports 5、Seasonal 5、Baby & kids 3（组数）

**Commercial ad**（6 种）：ecommerce 16、app_deal 14、desktop_page 13、launch 13、sampling_stand 12、product_info_poster 12（组数）

**Supplement**（16 种）：Vitamins & minerals 9、Omega-3 & fish oil 7、Immune support 5、Protein & sports 4、Prenatal 4、Botanicals 4、Collagen & beauty 3、Sleep & relaxation 3、Fibre 3、Women's health 2、Kids 2、Probiotics & gut 2、Eye health 2、Bone & joint 1、Coenzyme Q10 1、50+ multivitamin 1（组数）

**Event**（26 种）：Supplement info session 4、Seasonal pop-up 4、Charity bake sale 4、Product launch 3、Baking class 3、Health talk 3、Free health check 3、Chocolate workshop 3、Community supper 2、Food bank drive 2、Food festival 2、Cheese & bread tasting 2、Member day 2、Kids' cooking club 1、Nutrition workshop 1、Trade fair 1、Workplace wellness day 1、Cooking class 1、Store opening 1、Coffee cupping 1、Store anniversary 1、Christmas market 1、Campus health week 1、Farmers' market 1、In-store tasting 1、Food safety week 1（组数）

**Public-service poster**（20 种）：Salt reduction 4、Food fraud 3、Fridge & leftovers 3、Date labels 3、Supplement scams (older adults) 3、Allergen awareness 3、Water & hydration 3、Wild mushroom poisoning 3、Food safety at home 3、Reading nutrition labels 3、Food waste 2、Healthy drinks 2、Food bank & food poverty 2、Hand hygiene 2、Sugar reduction 2、Holiday food safety 2、School food 1、Healthy ageing nutrition 1、Infant feeding safety 1、Online food shopping 1（组数）

## 4. 地区

覆盖 **33** 个国家。按区域（组）：US 101、EU 90、UK 82、IE 50、CA 11。

按国家（组）：US 101、UK 82、IE 50、MT 16、CA 11、FR 3、LT 3、GR 3、PL 3、BE 3、IT 3、LU 3、ES 3、RO 3、FI 3、DE 3、SE 3、NO 3、HR 3、EE 3、CZ 3、DK 3、SK 3、SI 2、NL 2、CH 2、CY 2、IS 2、AT 2、BG 2、PT 2、HU 2、LV 2

| 类别 | CA | EU | IE | UK | US |
|---|---:|---:|---:|---:|---:|
| Food label | 0 | 12 | 24 | 34 | 34 |
| Commercial ad | 0 | 36 | 8 | 16 | 20 |
| Supplement | 0 | 4 | 8 | 14 | 27 |
| Event | 6 | 20 | 5 | 9 | 10 |
| Public-service poster | 5 | 18 | 5 | 9 | 10 |

## 5. 篡改类型

五个重点类型（含该类型的非 clean 样本数，共 668 条非 clean）：

| tamper_type | subtle | strong | 合计 |
|---|---:|---:|---:|
| efficacy_exaggeration | 44 | 76 | 120 |
| allergen_deletion | 41 | 56 | 97 |
| production_date_tamper | 32 | 58 | 90 |
| shelf_life_tamper | 35 | 59 | 94 |
| ingredient_order_tamper | 36 | 53 | 89 |

全部 29 种：

| tamper_type | 样本数 |
|---|---:|
| efficacy_exaggeration | 120 |
| allergen_deletion | 97 |
| shelf_life_tamper | 94 |
| production_date_tamper | 90 |
| ingredient_order_tamper | 89 |
| warning_deletion | 80 |
| price_tamper | 62 |
| nutrition_value_tamper | 61 |
| product_attribute_tamper | 60 |
| quota_contradiction | 59 |
| event_date_tamper | 53 |
| claim_nutrition_conflict | 51 |
| quantity_tamper | 44 |
| misinformation_insertion | 43 |
| hidden_fee_condition | 42 |
| health_fact_tamper | 39 |
| promotion_date_tamper | 37 |
| promotion_rule_tamper | 36 |
| manufacturer_info_tamper | 35 |
| contact_info_tamper | 31 |
| venue_tamper | 29 |
| regulatory_status_tamper | 27 |
| target_population_tamper | 25 |
| batch_number_tamper | 20 |
| source_attribution_tamper | 20 |
| agenda_time_conflict | 18 |
| function_upgrade | 15 |
| unsubstantiated_claim | 14 |
| storage_condition_tamper | 10 |

每条样本的篡改数：strong×2 = 75、strong×3 = 259、subtle×1 = 194、subtle×2 = 140

难度：clean/reference 334、strong/easy 197、strong/medium 137、subtle/hard 194、subtle/medium 140

单图可检测（single_image_detectable）：strong=True 334、subtle=False 30、subtle=True 304

## 6. 文本密度与载体

密度（「」内字符数；Low<200、Medium 200–499、High 500–1199、Very High≥1200）：Very High 749 (74.8%)、High 253 (25.2%)

画幅：3:4 219、4:5 210、4:3 183、9:16 177、16:9 165、1:1 48；真实感：flat 408、studio 276、phone 225、scene 93

## 7. 自动 QA（`python en/src/qa_en.py`）

结构与 clean 一致性错误数：**0**。精确重复 prompt：0。

各语义检查（解析 prompt 文本重新推导，不读引擎状态）：

| 检查 | clean 命中行数 | clean 违规 | subtle 违规 | strong 违规 |
|---|---:|---:|---:|---:|
| dates | 237 | 0 | 71 | 111 |
| eu_table | 121 | 0 | 8 | 25 |
| us_table | 54 | 0 | 2 | 8 |
| allergens | 184 | 0 | 30 | 45 |
| quid_order | 184 | 0 | 4 | 7 |
| claims | 63 | 0 | 16 | 31 |
| weekday | 166 | 0 | 28 | 0 |
| promo | 80 | 0 | 11 | 7 |
| agenda | 34 | 0 | 2 | 6 |
| event | 38 | 0 | 7 | 16 |

clean 组间 6-gram Jaccard（「」文本，全配对）：

| 类别 | 配对数 | 中位数 | p99 | 最大 |
|---|---:|---:|---:|---:|
| Commercial ad | 3160 | 0.021 | 0.093 | 0.286 |
| Event | 1225 | 0.0 | 0.025 | 0.62 |
| Food label | 5356 | 0.014 | 0.101 | 0.456 |
| Public-service poster | 1081 | 0.005 | 0.558 | 0.71 |
| Supplement | 1378 | 0.028 | 0.183 | 0.547 |

## 8. 人工抽检（LLM 审阅代理）

- review1：100 条，severity minor 72、major 28
- review2：100 条，severity minor 69、none 17、major 14
- review3：100 条，severity minor 67、none 23、major 10
- review4：100 条，severity minor 64、none 27、major 9
- review5：100 条，severity minor 57、none 35、major 8

每轮都从当时最新的完整 1002 条中重新随机抽 100 条（种子不同），由 4 个独立审阅代理按 `review*/RUBRIC.md` 逐条判定。每轮发现的缺陷类别都回到生成器或内容库修根本原因，并在 `qa_en.py` 中加入全量回归检查后再重新生成。

## 9. 第 4、5 轮之后的修复与回归检查

第 5 轮之后没有再做第 6 轮人工抽检；第 4、5 轮发现的缺陷类别改为用全量回归检查验证。下表中“修复前”是第 4 轮送审的版本，“修复后”是最终文件：

| 回归检查 | 修复前命中 | 修复后命中 |
|---|---:|---:|
| drop-in event with participant cap | 36 | 0 |
| allergen deletion leaves CAPITALS emphasis | 5 | 0 |
| Canadian row cites US agency | 4 | 0 |
| EU juice statement on US label | 3 | 0 |
| pharmacy venue for non-health event | 3 | 0 |
| N-month supply vs count/dose | 2 | 0 |
| ticket basis contradicts rules | 2 | 0 |
| event on Christmas Day / New Year's Day | 1 | 0 |
| slice larger than half the pack | 1 | 0 |
| Canadian row with Fahrenheit only | 1 | 0 |
| multipack piece weight vs portion | 1 | 0 |

第 5 轮发现、但只出现在单个原型里的问题直接改了内容库：penne 名称配 fusilli 外观，含片写成咀嚼片，马德里地址用了加泰罗尼亚语街名和不存在的邮编。另外，篡改算子在判定“不适用”之前已经改了字段，留下没有记录在 tamper_details 里的改动；现在引擎会把这类改动回滚。

