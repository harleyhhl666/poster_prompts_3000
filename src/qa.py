"""QA for generated prompt files. Usage: python src/qa.py path/to/poster_prompts_N.jsonl [--sample 100]
Writes <stem>_qa.json with all findings + a random sample file for manual review."""
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
import difflib

sys.path.insert(0, os.path.dirname(__file__))
from validate_libs import REAL_BRANDS
from qa_review_checks import review_checks

LEFTOVER = ["TODO", "这里填写", "XXXX", "XXX", "{brand}", "{org}", "None", "null", "nan", "占位", "待定", "示例文字", "[", "]", "{", "}"]
CORE_TYPES = ["efficacy_exaggeration", "allergen_deletion", "production_date_tamper", "shelf_life_tamper", "ingredient_order_tamper"]


RULE_MARK = "本提示词中「」内的内容为必须逐字呈现的文字"
AMBIG = {"统一", "光明", "修正", "999", "每日", "晨光", "田园", "北纬", "正大", "中粮", "长寿花"}


def quoted(p):
    p = p.split(RULE_MARK)[0]
    return re.findall("「(.*?)」", p, flags=re.S)


import datetime as _dt
from common import add_months, add_days, NRV
NAME2KEY = {"能量": "energy", "蛋白质": "protein", "脂肪": "fat", "碳水化合物": "carb", "钠": "sodium", "钙": "calcium",
            "膳食纤维": "fiber", "维生素C": "vitc", "铁": "iron", "钾": "potassium", "维生素D": "vitd", "锌": "zinc", "维生素A": "vita",
            "—饱和脂肪": "sat"}


def _pd(s):
    s = s.strip()
    for f in ("%Y年%m月%d日", "%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return _dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    return None


def semantic(p):
    """Returns list of inconsistency codes found in the prompt text (expected empty for clean)."""
    bad = []
    q = quoted(p)
    txt = "\n".join(q)
    m1 = re.search(r"生产日期[：】]([^」；\n]+)", txt)
    m2 = re.search(r"保质期[：】](\d+)(个月|天)", txt)
    m3 = re.search(r"保质期至[：】]([^」；\n]+)", txt)
    if m1 and m2 and m3:
        a, c = _pd(m1.group(1)), _pd(m3.group(1))
        n = int(m2.group(1))
        if a and c:
            exp = add_days(add_months(a, n), -1) if m2.group(2) == "个月" else add_days(a, n - 1)
            if exp != c:
                bad.append("date_shelf_expiry_mismatch")
        # batch date segment
        mb = re.search(r"(?:批号|LOT|生产批次|生产批号)[：】]([A-Z0-9\-]+)", txt)
        if a and mb:
            b = mb.group(1)
            if not any(a.strftime(f) in b for f in ("%y%m%d", "%Y%m%d", "%Y-%m-%d")):
                bad.append("batch_date_mismatch")
    for m in re.finditer(r"(\d{4})年(\d{1,2})月(\d{1,2})日（周(.)）", txt):
        d = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if "一二三四五六日"[d.weekday()] != m.group(4):
            bad.append("weekday_wrong")
    rows = {}
    for m in re.finditer(r"「([^｜」]+)｜([\d.]+) (kJ|g|mg|μg|μgRE)｜(\d+%|—)」", p):
        name, v, u, pct = m.groups()
        k = NAME2KEY.get(name)
        rows[name] = (float(v), u)
        if k in NRV and pct != "—":
            exp = int(round(float(v) / NRV[k] * 100))
            if abs(exp - int(pct[:-1])) > 1:
                bad.append("nrv_mismatch")
        if name in ("钠", "钙") and u != "mg":
            bad.append("unit_wrong")
    if all(k in rows for k in ("能量", "蛋白质", "脂肪", "碳水化合物")):
        e = rows["能量"][0]
        calc = 17 * rows["蛋白质"][0] + 37 * rows["脂肪"][0] + 17 * rows["碳水化合物"][0] + 8 * rows.get("膳食纤维", (0,))[0]
        if e > 30 and abs(calc - e) / e > 0.12:
            bad.append("energy_inconsistent")
    return sorted(set(bad))


def check(path, n_sample=100):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    F = defaultdict(list)
    ids = Counter(r["id"] for r in rows)
    for k, v in ids.items():
        if v > 1:
            F["dup_id"].append(k)
    groups = defaultdict(list)
    for r in rows:
        groups[r["group_id"]].append(r)
    for g, rs in groups.items():
        vs = sorted(x["variant"] for x in rs)
        if vs != ["clean", "strong", "subtle"]:
            F["bad_triplet"].append(g)
        cats = {x["super_category"] for x in rs}
        prods = {x["product_or_title"].split(" ")[0] for x in rs}
        brands = {x["brand_or_organizer"] for x in rs}
        lays = {(x["layout"], x["aspect_ratio"], x["visual_style"]) for x in rs}
        if len(cats) > 1 or len(brands) > 1 or len(lays) > 1:
            F["triplet_inconsistent"].append(g)
        by = {x["variant"]: x for x in rs}
        if len(by) == 3:
            c, s, t = by["clean"]["prompt"], by["subtle"]["prompt"], by["strong"]["prompt"]
            if c == s or c == t or s == t:
                F["triplet_identical_prompt"].append(g)
            qc, qs = quoted(c), quoted(s)
            if qc == qs:
                F["subtle_no_quoted_change"].append(g)
    for r in rows:
        p = r["prompt"]
        v = r["variant"]
        if v not in ("clean", "subtle", "strong"):
            F["bad_variant"].append(r["id"])
        if not p or len(p) < 600:
            F["prompt_short"].append((r["id"], len(p)))
        qtext = "\n".join(quoted(p))
        for w in LEFTOVER:
            body = qtext if w not in ("[", "]", "{", "}") else p
            if w in ("[", "]", "{", "}"):
                if w in body:
                    F["leftover_bracket"].append((r["id"], w))
            elif w in body:
                F["leftover_token"].append((r["id"], w))
        if p.count("「") != p.count("」"):
            F["unbalanced_quote"].append(r["id"])
        for a, b in ("（）", "()", "【】"):
            if p.count(a) != p.count(b):
                F["unbalanced_paren"].append((r["id"], a + b))
        for q in quoted(p):
            if not q.strip():
                F["empty_quote"].append(r["id"])
            if "None" in q:
                F["none_in_quote"].append(r["id"])
        for b in REAL_BRANDS:
            if b in AMBIG:
                continue
            if b in qtext:
                F["real_brand"].append((r["id"], b))
        if v == "clean":
            if r["tamper_types"] or r["tampered_fields"]:
                F["clean_has_tamper"].append(r["id"])
            if "刻意与其他字段不一致" in p:
                F["clean_has_anomaly_note"].append(r["id"])
        else:
            if not r["tamper_types"] or not r["tampered_fields"]:
                F["tamper_missing"].append(r["id"])
        if "不得使用乱码" not in p or "清晰、完整、可辨认" not in p:
            F["missing_text_rule"].append(r["id"])
        # field presence for label-type items
        if r["super_category"] in ("食品标签",):
            for need in ["配料：", "生产日期：", "保质期：", "保质期至：", "营养成分表", "净含量", "贮存条件："]:
                if need not in p:
                    F["label_missing_field"].append((r["id"], need))
            if not re.search(r"(批号|LOT|生产批次)：", p):
                F["label_missing_field"].append((r["id"], "批号"))
            if v == "clean" and "产品标准代号：" not in p and "原产国：" not in p:
                F["label_missing_field"].append((r["id"], "标准号"))
        if r["super_category"] == "商业广告":
            for need in ["配料：", "生产日期：", "活动时间", "营养成分表", "¥"]:
                if need not in p:
                    F["ad_missing_field"].append((r["id"], need))
        if r["super_category"] == "保健品说明":
            for need in ["生产日期", "保质期至", "产品标准号", "适宜人群"]:
                if need not in p:
                    F["supp_missing_field"].append((r["id"], need))
        sem = semantic(p)
        rv = review_checks(r)
        r["_rv"] = rv
        if rv:
            F["review_defect_" + ("clean" if v == "clean" else "tampered")].append((r["id"], rv))
        r["_sem"] = sem
        if v == "clean" and sem:
            F["clean_semantic_inconsistency"].append((r["id"], sem))
        # clean logical checks
        if v == "clean":
            m = re.search(r"生产日期：(\S+?)」", p)
            # allergen present check: if 配料 has 牛乳/乳粉/小麦粉/大豆 etc but no allergen text
            ing = re.search(r"配料：(.*?)。」", p)
            if ing and r["super_category"] in ("食品标签", "商业广告"):
                txt = ing.group(1).replace("鸡蛋花", "")
                trig = [w for w in ["小麦粉", "全脂乳粉", "脱脂乳粉", "生牛乳", "花生", "鸡蛋", "大豆", "虾", "乳清"] if w in txt]
                refined = [w for w in ["精炼大豆油", "大豆磷脂"] if w in txt]
                if trig and not any(k in p for k in ["过敏原", "致敏物质"]):
                    if not (set(trig) <= {"大豆"} and refined):
                        F["clean_allergen_missing"].append((r["id"], trig))
            for bad in ([] if r["super_category"] == "公益海报" else ["根治", "治愈", "三天见效", "药到病除", "替代药物", "停药"]):
                qs = "".join(quoted(p))
                if bad in qs and "不能代替药物" not in bad:
                    F["clean_contains_exaggeration"].append((r["id"], bad))
    # duplicates: exact + near dup on quoted text (per super_category, sample-based)
    exact = Counter(r["prompt"] for r in rows)
    F["exact_dup_prompts"] = [k[:60] for k, v in exact.items() if v > 1]
    rng = random.Random(7)
    near = []
    by_cat = defaultdict(list)
    for r in rows:
        if r["variant"] == "clean":
            by_cat[r["super_category"]].append(r)
    max_sims = {}
    for cat, rs in by_cat.items():
        texts = [("".join(quoted(r["prompt"])), r["group_id"]) for r in rs]
        pairs = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                pairs.append((i, j))
        rng.shuffle(pairs)
        pairs = pairs[:3000]
        sims = []
        for i, j in pairs:
            a, b = texts[i][0], texts[j][0]
            s = difflib.SequenceMatcher(None, a, b, autojunk=False).quick_ratio()
            if s > 0.8:
                s = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
            sims.append(s)
            if s > 0.85:
                near.append((texts[i][1], texts[j][1], round(s, 3)))
        sims.sort()
        max_sims[cat] = {"pairs_checked": len(sims), "median": round(sims[len(sims) // 2], 3) if sims else None,
                         "p99": round(sims[int(len(sims) * 0.99)], 3) if sims else None, "max": round(sims[-1], 3) if sims else None}
    F["near_dup_pairs_gt_0.85"] = near
    # diversity stats
    stats = {
        "n_rows": len(rows), "n_groups": len(groups),
        "variant": Counter(r["variant"] for r in rows),
        "super_category": Counter(r["super_category"] for r in rows),
        "n_sub_category": len({(r["super_category"], r["sub_category"]) for r in rows}),
        "density": Counter(r["text_density"] for r in rows),
        "aspect": Counter(r["aspect_ratio"] for r in rows),
        "realism": Counter(r["realism"] for r in rows),
        "unique_brands": len({r["brand_or_organizer"] for r in rows}),
        "unique_products": len({r["product_or_title"] for r in rows}),
        "unique_archetypes": len({r["source_archetype"] for r in rows}),
        "prompt_len": {"min": min(len(r["prompt"]) for r in rows), "max": max(len(r["prompt"]) for r in rows),
                       "mean": round(sum(len(r["prompt"]) for r in rows) / len(rows))},
        "similarity_clean_quoted_text": max_sims,
    }
    tt = Counter()
    for r in rows:
        for t in r["tamper_types"]:
            tt[(t, r["variant"])] += 1
    stats["tamper_by_variant"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(tt.items())}
    semc = Counter()
    for r in rows:
        for s in r.get("_sem", []):
            semc[(r["variant"], s)] += 1
    stats["semantic_inconsistency_by_variant"] = {f"{a}|{b}": c for (a, b), c in sorted(semc.items())}
    rvc = Counter()
    for r in rows:
        for x in r.get("_rv", []):
            rvc[x] += 1
    stats["review_defect_counts"] = dict(rvc)
    for r in rows:
        r.pop("_sem", None)
        r.pop("_rv", None)
    summary = {k: len(v) for k, v in F.items()}
    out = {"summary": summary, "stats": stats, "findings": {k: v[:50] for k, v in F.items()}}
    stem = os.path.splitext(path)[0]
    json.dump(out, open(stem + "_qa.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    # random sample for manual review
    samp = random.Random(2026).sample(rows, min(n_sample, len(rows)))
    with open(stem + f"_sample{len(samp)}.jsonl", "w", encoding="utf-8") as f:
        for r in samp:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"summary": summary, "stats": {k: v for k, v in stats.items() if k != "tamper_by_variant"}}, ensure_ascii=False, indent=1, default=str))
    return out


if __name__ == "__main__":
    n = 100
    if "--sample" in sys.argv:
        n = int(sys.argv[sys.argv.index("--sample") + 1])
    check(sys.argv[1], n)
