"""Build en/poster_prompt_generation_report_en.md from the final English JSONL + QA json + review verdicts."""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CORE = ["efficacy_exaggeration", "allergen_deletion", "production_date_tamper", "shelf_life_tamper", "ingredient_order_tamper"]
CN = {"Food label": "食品标签", "Commercial ad": "商业广告", "Supplement": "保健品说明", "Event": "活动宣传", "Public-service poster": "公益海报"}


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    path = os.path.join(ROOT, "final", "poster_prompts_en_1002.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    qa = json.load(open(os.path.join(ROOT, "final", "poster_prompts_en_1002_qa.json"), encoding="utf-8"))
    L = ["# 英文部分生成报告（自动生成：`python en/src/make_report_en.py`）", ""]
    L.append("## 1. 总量\n")
    g = {r["group_id"] for r in rows}
    L.append("共 **%d** 条提示词，**%d** 个三联组（clean/subtle/strong 各 %d 条），ID `%s`–`%s`。\n" % (
        len(rows), len(g), len(g), rows[0]["id"], rows[-1]["id"]))
    L.append("## 2. 一级类别\n")
    c = Counter(r["super_category"] for r in rows)
    L.append(table(["super_category", "中文对应", "组", "条"], [[k, CN[k], c[k] // 3, c[k]] for k in CN] + [["合计", "", len(g), len(rows)]]) + "\n")
    L.append("## 3. 二级类别\n")
    for k in CN:
        s = Counter(r["sub_category"] for r in rows if r["super_category"] == k and r["variant"] == "clean")
        L.append("**%s**（%d 种）：" % (k, len(s)) + "、".join("%s %d" % (a, b) for a, b in s.most_common()) + "（组数）\n")
    L.append("## 4. 地区\n")
    cc = Counter(r["country"] for r in rows if r["variant"] == "clean")
    rg = Counter(r["region"] for r in rows if r["variant"] == "clean")
    L.append("覆盖 **%d** 个国家。按区域（组）：" % len(cc) + "、".join("%s %d" % x for x in rg.most_common()) + "。\n")
    L.append("按国家（组）：" + "、".join("%s %d" % x for x in cc.most_common()) + "\n")
    per = defaultdict(Counter)
    for r in rows:
        if r["variant"] == "clean":
            per[r["super_category"]][r["region"]] += 1
    L.append(table(["类别"] + sorted(rg), [[k] + [per[k][x] for x in sorted(rg)] for k in CN]) + "\n")
    L.append("## 5. 篡改类型\n")
    t = Counter(x for r in rows for x in set(r["tamper_types"]))
    L.append("五个重点类型（含该类型的非 clean 样本数，共 %d 条非 clean）：\n" % sum(1 for r in rows if r["variant"] != "clean"))
    L.append(table(["tamper_type", "subtle", "strong", "合计"], [[k, sum(1 for r in rows if r["variant"] == "subtle" and k in r["tamper_types"]),
                                                                   sum(1 for r in rows if r["variant"] == "strong" and k in r["tamper_types"]), t[k]] for k in CORE]) + "\n")
    L.append("全部 %d 种：\n" % len(t))
    L.append(table(["tamper_type", "样本数"], [[k, v] for k, v in t.most_common()]) + "\n")
    n = Counter((r["variant"], len(r["tamper_types"])) for r in rows if r["variant"] != "clean")
    L.append("每条样本的篡改数：" + "、".join("%s×%d = %d" % (a, b, v) for (a, b), v in sorted(n.items())) + "\n")
    d = Counter((r["variant"], r["difficulty"]) for r in rows)
    L.append("难度：" + "、".join("%s/%s %d" % (a, b, v) for (a, b), v in sorted(d.items())) + "\n")
    s = Counter((r["variant"], r["single_image_detectable"]) for r in rows if r["variant"] != "clean")
    L.append("单图可检测（single_image_detectable）：" + "、".join("%s=%s %d" % (a, b, v) for (a, b), v in sorted(s.items(), key=str)) + "\n")
    L.append("## 6. 文本密度与载体\n")
    dn = Counter(r["text_density"] for r in rows)
    L.append("密度（「」内字符数；Low<200、Medium 200–499、High 500–1199、Very High≥1200）：" + "、".join("%s %d (%.1f%%)" % (k, v, 100 * v / len(rows)) for k, v in dn.most_common()) + "\n")
    ar = Counter(r["aspect_ratio"] for r in rows)
    L.append("画幅：" + "、".join("%s %d" % x for x in ar.most_common()) + "；真实感：" + "、".join("%s %d" % x for x in Counter(r["realism"] for r in rows).most_common()) + "\n")
    L.append("## 7. 自动 QA（`python en/src/qa_en.py`）\n")
    L.append("结构与 clean 一致性错误数：**%d**。精确重复 prompt：%d。\n" % (len(qa["errors"]), qa["exact_duplicate_prompts"]))
    rows_q = []
    for k, v in qa["checks"].items():
        rows_q.append([k, v.get("matched_clean", 0), v.get("viol_clean", 0), v.get("viol_subtle", 0), v.get("viol_strong", 0)])
    L.append("各语义检查（解析 prompt 文本重新推导，不读引擎状态）：\n")
    L.append(table(["检查", "clean 命中行数", "clean 违规", "subtle 违规", "strong 违规"], rows_q) + "\n")
    L.append("clean 组间 6-gram Jaccard（「」文本，全配对）：\n")
    L.append(table(["类别", "配对数", "中位数", "p99", "最大"], [[k, v["pairs"], v["median"], v["p99"], v["max"]] for k, v in qa["dup_6gram_jaccard_clean"].items()]) + "\n")
    L.append("## 8. 人工抽检（LLM 审阅代理）\n")
    for rd in sorted(glob.glob(os.path.join(ROOT, "final", "review*"))):
        vs = []
        for f in glob.glob(os.path.join(rd, "verdict*.jsonl")):
            vs += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
        if vs:
            sv = Counter(v.get("severity") for v in vs)
            L.append("- %s：%d 条，severity " % (os.path.basename(rd), len(vs)) + "、".join("%s %d" % x for x in sv.most_common()))
    L.append("")
    L.append("每轮都从当时最新的完整 1002 条中重新随机抽 100 条（种子不同），由 4 个独立审阅代理按 `review*/RUBRIC.md` 逐条判定。"
             "每轮发现的缺陷类别都回到生成器或内容库修根本原因，并在 `qa_en.py` 中加入全量回归检查后再重新生成。\n")
    rp = os.path.join(ROOT, "final", "review5", "post_fix_regression.json")
    if os.path.exists(rp):
        rg = json.load(open(rp, encoding="utf-8"))
        L.append("## 9. 第 4、5 轮之后的修复与回归检查\n")
        L.append("第 5 轮之后没有再做第 6 轮人工抽检；第 4、5 轮发现的缺陷类别改为用全量回归检查验证。"
                 "下表中“修复前”是第 4 轮送审的版本，“修复后”是最终文件：\n")
        L.append(table(["回归检查", "修复前命中", "修复后命中"], [[k, v["before"], v["after"]] for k, v in rg["classes"].items()]) + "\n")
        L.append("第 5 轮发现、但只出现在单个原型里的问题直接改了内容库：penne 名称配 fusilli 外观，含片写成咀嚼片，马德里地址用了加泰罗尼亚语街名和不存在的邮编。"
                 "另外，篡改算子在判定“不适用”之前已经改了字段，留下没有记录在 tamper_details 里的改动；现在引擎会把这类改动回滚。\n")
    open(os.path.join(ROOT, "poster_prompt_generation_report_en.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("report written")


if __name__ == "__main__":
    main()
