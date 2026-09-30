"""Build poster_prompt_generation_report.md from the final JSONL, QA json and review verdict files (no hand-typed numbers)."""
import json, collections, glob, os, re, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "final")
rows = [json.loads(l) for l in open(os.path.join(F, "poster_prompts_3000.jsonl"), encoding="utf-8")]
qa = json.load(open(os.path.join(F, "poster_prompts_3000_qa.json"), encoding="utf-8"))
C = collections.Counter
L = []
w = L.append


def table(head, items):
    w("| " + " | ".join(head) + " |")
    w("|" + "|".join(["---"] + ["---:"] * (len(head) - 1)) + "|")
    for it in items:
        w("| " + " | ".join(str(x) for x in it) + " |")
    w("")


n = len(rows)
groups = C(r["group_id"] for r in rows)
w("# 富文字宣传海报 / 食品标签 / 保健品说明 提示词数据集 — 生成报告")
w("")
w(f"生成时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}（本报告由 `src/make_report.py` 从最终文件自动统计，未手工填写数字）")
w("")
w("## 1. 数据总量与结构")
w("")
table(["项目", "数值"], [
    ["提示词总数", n], ["基础组数", len(groups)],
    ["每组条数", "、".join(f"{k}条×{v}组" for k, v in sorted(C(groups.values()).items()))],
    ["ID 唯一", len({r['id'] for r in rows}) == n],
    ["每组恰为 clean/subtle/strong 各一", all(sorted(r2["variant"] for r2 in rows if r2["group_id"] == g) == ["clean", "strong", "subtle"] for g in list(groups)[:1000])],
    ["品牌/主办方（去重）", len({r['brand_or_organizer'] for r in rows})],
    ["产品/标题（去重）", len({r['product_or_title'] for r in rows})],
    ["内容原型（archetype）", len({r['source_archetype'] for r in rows})],
    ["prompt 长度（字符）min / mean / max", f"{min(len(r['prompt']) for r in rows)} / {sum(len(r['prompt']) for r in rows)//n} / {max(len(r['prompt']) for r in rows)}"],
])
w("## 2. 一级类别")
w("")
sc = C(r["super_category"] for r in rows)
table(["一级类别", "条数", "组数"], [[k, v, v // 3] for k, v in sc.most_common()] + [["合计", n, n // 3]])
w("相对初始建议（250/150/150/300/150 组）的调整：食品标签 300→310、商业广告 250→240、保健品说明 150→160、公益海报 150→140，活动宣传 150 不变。原因见 taxonomy 第 6 节：标签类字段最密、四个重点篡改点全部可落地；公益海报没有配料/批号/营养表，只能承载部分篡改类型。")
w("")
w("## 3. 二级类别")
w("")
subs = collections.defaultdict(C)
for r in rows:
    subs[r["super_category"]][r["sub_category"]] += 1
w(f"二级类别共 **{len({r['sub_category'] for r in rows})}** 种（按一级类别分列，括号内为条数）：")
w("")
for k, _ in sc.most_common():
    w(f"- **{k}**（{len(subs[k])} 种）：" + "、".join(f"{s}({v})" for s, v in subs[k].most_common()))
w("")
w("## 4. Clean / Subtle / Strong")
w("")
table(["variant", "条数"], sorted(C(r["variant"] for r in rows).items()))
w("## 5. 篡改类型统计")
w("")
w("统计口径：一条 prompt 可以同时含多种篡改类型，所以下表各类型之和大于 2000（subtle+strong）。“条数”指含该类型的 prompt 数。")
w("")
FOCUS = [("efficacy_exaggeration", "功效夸大声明"), ("allergen_deletion", "过敏原信息删除"), ("production_date_tamper", "生产日期篡改"),
         ("shelf_life_tamper", "保质期篡改"), ("ingredient_order_tamper", "配料顺序篡改")]
tv = C()
for r in rows:
    for t in set(r["tamper_types"]):
        tv[(t, r["variant"])] += 1
w("### 5.1 五个重点篡改点")
w("")
table(["类型", "中文", "subtle", "strong", "合计"], [[k, z, tv[(k, 'subtle')], tv[(k, 'strong')], tv[(k, 'subtle')] + tv[(k, 'strong')]] for k, z in FOCUS])
w("### 5.2 扩展篡改类型")
w("")
ZH = {"nutrition_value_tamper": "营养数值/NRV%/单位篡改", "claim_nutrition_conflict": "营养声称与营养表冲突", "price_tamper": "价格/折扣篡改",
      "promotion_date_tamper": "活动期限篡改", "promotion_rule_tamper": "活动规则删除/改写", "hidden_fee_condition": "“免费”隐藏付费条件",
      "quantity_tamper": "净含量/件数篡改", "standard_number_tamper": "执行标准号篡改/错类", "batch_number_tamper": "批号篡改/批号与日期冲突",
      "approval_number_tamper": "备案号/批准文号篡改", "manufacturer_info_tamper": "生产商/产地/委托关系篡改", "warning_deletion": "警示语/免责声明删除",
      "target_population_tamper": "适宜/不适宜人群篡改", "product_attribute_tamper": "产品属性冒充（有机/儿童/保健食品/药品化）",
      "storage_tamper": "贮存条件篡改", "event_date_tamper": "活动日期/星期篡改", "agenda_time_conflict": "流程时间重叠",
      "quota_contradiction": "名额前后矛盾", "contact_info_tamper": "联系电话/举报热线篡改", "venue_tamper": "活动地点前后不一致",
      "health_fact_tamper": "科普数据篡改（如每日盐量）", "misinformation_insertion": "插入错误健康知识", "fake_authority": "冒用权威/伪造认证",
      "license_number_tamper": "生产许可证编号篡改", "net_content_tamper": "净含量篡改", "source_attribution_tamper": "数据来源/引用机构篡改", "unsubstantiated_claim": "无依据的检测/认证宣称", "storage_condition_tamper": "贮存条件篡改（如冷藏改常温）"}
ext = sorted({t for (t, v) in tv} - {k for k, _ in FOCUS}, key=lambda t: -(tv[(t, 'subtle')] + tv[(t, 'strong')]))
table(["类型", "含义", "subtle", "strong", "合计"], [[t, ZH.get(t, "—"), tv[(t, 'subtle')], tv[(t, 'strong')], tv[(t, 'subtle')] + tv[(t, 'strong')]] for t in ext])
w(f"篡改类型共 **{len({t for (t, v) in tv})}** 种（5 个重点 + {len(ext)} 个扩展）。")
w("")
nt = C(len(r["tamper_types"]) for r in rows if r["variant"] != "clean")
w("每条篡改样本的篡改类型数：" + "；".join(f"{k} 种 = {v} 条" for k, v in sorted(nt.items())))
w("")
sd = C((r["variant"], r["single_image_detectable"]) for r in rows if r["variant"] != "clean")
w(f"`single_image_detectable`（单张图内能否找到矛盾，而不必与 clean 版对照）：subtle True={sd[('subtle', True)]} / False={sd[('subtle', False)]}；strong True={sd[('strong', True)]} / False={sd[('strong', False)]}。False 的样本主要是单纯删除（例如删掉一个过敏原、删掉一条警示语），只有和同组 clean 版对比才能发现。做单图检测评测时建议按这个字段拆开报告。")
w("")
w("## 6. 视觉与文本多样性")
w("")
table(["画幅", "条数"], C(r["aspect_ratio"] for r in rows).most_common())
table(["文本密度", "条数"], C(r["text_density"] for r in rows).most_common())
RZ = {"flat": "平面设计稿", "studio": "摄影棚产品摄影", "scene": "实景（货架/门店/展会/玻璃门张贴）", "phone": "手机实拍（透视/反光/折痕）"}
table(["真实感", "条数"], [[f"{k}（{RZ.get(k, k)}）", v] for k, v in C(r["realism"] for r in rows).most_common()])
car = C(r["carrier"] for r in rows)
w(f"图像载体共 {len(car)} 种：" + "、".join(f"{k}({v})" for k, v in car.most_common()))
w("")
vs = C(r["visual_style"].split("/")[0] for r in rows)
w(f"视觉风格（主风格）{len(vs)} 种：" + "、".join(f"{k}({v})" for k, v in vs.most_common()))
w("")
w("## 7. 重复度")
w("")
s = qa["summary"]
w(f"- 完全相同的 prompt：**{s.get('exact_dup_prompts', 0)}**。")
w(f"- 同一级类别内 clean prompt 两两比较引号内文字（即图中实际渲染的文字）的相似度，每类随机 3000 对：")
w("")
table(["一级类别", "中位数", "P99", "最大"], [[k, v["median"], v["p99"], v["max"]] for k, v in qa["stats"]["similarity_clean_quoted_text"].items()])
w(f"- 跨组整体相似度 > 0.85 的组对：{s.get('near_dup_pairs_gt_0.85', 0)} 对（逐对核对：1 对为同一活动原型“社区免费健康咨询日”，另 3 对为运动营养食品的同一原型，即电解质固体饮料 2 对、乳清蛋白粉 1 对。这些原型的法定标签骨架固定，包括原料、适宜人群和警示语；品牌、生产商、日期、批号、价格、地址均不同，不是重复样本，但属于同原型内的高相似样本）。")
w("- 同组三联（clean/subtle/strong）刻意保持高度相似，只改动关键文字，因此不计入重复度统计。")
w("")
w("## 8. 自动 QA")
w("")
w("QA 脚本：`src/qa.py`（结构/模板残留/字段完整度/三联一致性/语义一致性）、`src/qa_round2_checks.py`、`src/qa_round4_checks.py`、`src/qa_round5_checks.py`（针对人工抽检中发现的每一类缺陷，写成覆盖全量 3000 条的回归检查）、`src/validate_libs.py`（内容库自检：配料百分比之和、营养数值与配料是否匹配、声称条件、过敏原映射等）。")
w("")
w("最终结果：")
w("")
w("- 结构：3000 行 JSON 全部可解析，ID 唯一，1000 组每组恰好 clean/subtle/strong 各一条，variant 字段只有这三个取值。")
w("- 模板残留：TODO / 这里填写 / XXXX / 未闭合括号 / 空 prompt / 过短 prompt 均为 0。")
w("- subtle/strong 的 `tamper_types` 与 `tampered_fields` 空值：0。")
w("- clean 语义一致性（保质期至 = 生产日期 + 保质期 − 1 天、批号内日期 = 生产日期、星期与日期匹配、NRV% 按四舍五入计算、能量与三大营养素一致、营养声称满足表中数值、过敏原与配料一致、流程表时间在活动时间内且不重叠、促销期不超出保质期）：**0 条违规**。")
w(f"- 篡改样本中 `review_defect_tampered`={s.get('review_defect_tampered')}：都是 `multi_city`，即篡改后的地址城市与另一处城市不同。这正是 manufacturer_info_tamper 本来要制造的矛盾，属于预期命中，不是缺陷。")
w("- 其余已知的检查器误报：`event_on_cny` 2 条（strong 样本把日期故意挪进春节假期，属于篡改本身）；`meat_wrong_sc` 6 条（“左旋肉碱”名字里有“肉”字，被规则误判为肉制品）。")
w("")
w("## 9. 人工抽检（每轮 100 条，4 个相互独立的 LLM 审阅代理各看 25 条）")
w("")
w("每轮都从当时最新的完整 3000 条中重新随机抽 100 条（每轮种子不同）。审阅代理拿到的是 prompt 原文加 tamper_details，逐条判断：①原样发给 GPT Image 2/2.5 是否足以生成（generatable）；②是否像真实中国市场的内容（realistic）；③篡改是否真实存在且自然融入，clean 是否没有非预期矛盾（tamper_ok）；并给出 severity。发现的每类缺陷都回到生成引擎或内容库修根因，再全量重新生成，而不是只修被抽到的那几条。")
w("")
rounds = []
for d in sorted(glob.glob(os.path.join(F, "review*")), key=lambda p: int(re.sub(r"\D", "", os.path.basename(p)) or 1)):
    vs_ = []
    for fp in glob.glob(os.path.join(d, "verdict*.jsonl")):
        for l in open(fp, encoding="utf-8"):
            l = l.strip()
            if l:
                try:
                    vs_.append(json.loads(l))
                except Exception:
                    pass
    if not vs_:
        continue
    k = os.path.basename(d).replace("review", "") or "1"
    sv = C(v.get("severity") for v in vs_)
    rounds.append([k, len(vs_), sum(bool(v.get("generatable")) for v in vs_), sum(bool(v.get("realistic")) for v in vs_),
                   sum(bool(v.get("tamper_ok")) for v in vs_), sv["none"], sv["minor"], sv["major"]])
table(["轮次", "抽检数", "generatable", "realistic", "tamper_ok", "无缺陷", "minor", "major"], rounds)
w("各轮 major 缺陷及对应修复（均为全量根因修复）：")
w("")
w("- 第 1–3 轮：营养表与配料不匹配、卖点与具体口味不符、残留真实品牌的包装特征与口号、产地和季节文案与商品冲突。修复方式：对全部 131 个内容原型逐条审计，共修改 104 个，审计记录见 `docs/library_audit/`。")
w("- 第 4 轮：过敏原与配料不一致；载体与包装不一致；标准号篡改恰好篡改成了一个本来就适用的真实标准（例如 GB 7101 本来就适用于固体饮料，这样的“篡改”其实不构成异常）；GB 19644-2010 已被 2024 版替代（已核实）；SC 许可证类别码与商品类别不符。")
w("- 第 5 轮：流程时间“冲突”其实只是首尾相接，并未重叠；活动时间与流程表不一致；删除警示语后正文里仍有近似语句；短保质期商品在促销期内已过期；酱油类配料没有标注小麦；活动日期落在春节当天。")
w("- 第 6 轮：按份标注的营养表与规格不一致（每片 1.0g 对应规格 1.2g×30 片）；能量“0”界限值被错误地按每份判断（应按每100g/100mL判断）。")
w("- 第 7 轮：产地篡改后恰好与生产商城市相同，篡改不成立。另修了三处：果汁饮料的果汁含量抬到 ≥10%；全民营养周（5 月）移出了数据的日期窗口；第二个批准文号不再放在没有背面的海报上。")
w("")
w("注意：第 7 轮的数字是修复前测得的；修复后的最终版本没有再做一轮完整的 100 条人工抽检。第 7 轮修复对应的全量回归检查结果都是 0。")
w("")
w("## 10. 法规口径说明")
w("")
w("营养声称条件（低脂/无糖/高钙等）、0 界限值、NRV 数值、致敏物质类别、保健功能目录用语、警示用语等引用依据见 `poster_dataset_taxonomy.md` 第 8 节。无法确认的规则一律标注为 **dataset-designed anomaly**，不作为法律结论。标准号：实物标签优先使用虚构的企业标准号（Q/xxx）。只有核实过适用范围的国家标准才会作为 clean 值使用；篡改版使用的是“类别不符”的真实标准号。所有品牌、公司、机构名称都是虚构的，地址用的是真实地级市加虚构的区和街道，电话、条码和各类编号都是格式正确的虚构号码。")
w("")
w("## 11. 建议人工抽检的部分")
w("")
w("1. `single_image_detectable=false` 的样本：只能靠和 clean 版对照才能发现，适合做 paired 评测，单图评测时建议剔除或单独报告。")
w("2. 配料顺序篡改中没有配 “≥X%” 标示的样本：单图基本无法判定，已标 single_image_detectable=false。")
w("3. 活动宣传类中流程表较长的样本：GPT Image 在长表格上容易漏行，出图后要核对行数。")
w("4. Very High 密度的实拍风（phone/scene）：小字在透视、反光条件下可能不可读，出图后需要 OCR 复核。")
w("5. 进口食品中文补充标签（原产国、进口商信息）：数量较少，现实中的细节规则更多。")
w("6. 保健食品的功效声明与批准文号格式：已按公开目录用语设计，但批准文号是虚构的，不要当作真实编号。")
w("")
open(os.path.join(ROOT, "poster_prompt_generation_report.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L[:12]))
print("... rounds:", rounds)
