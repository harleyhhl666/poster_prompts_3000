"""Measure round-2 defect classes on the regenerated 3000 (automatable subset)."""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_review_checks import quoted
from consistency import kw_missing, has_place
import brands as B

rows = [json.loads(l) for l in open("final/poster_prompts_3000.jsonl", encoding="utf-8")]
C = collections.Counter()
ex = collections.defaultdict(list)


def hit(k, r):
    C[k] += 1
    if len(ex[k]) < 3:
        ex[k].append(r["id"])


code_city = {v: k for k, v in B.CITY_CODE.items()}
for r in rows:
    p = r["prompt"]
    q = quoted(p)
    t = "\n".join(q)
    head = p.split("\n")[0] + p.split("\n")[1]
    ing = re.search(r"(?:配料|原料)[：】]([^」]+)", t)
    il = ing.group(1) if ing else ""
    # SC licence region vs manufacturer city
    for m in re.finditer(r"SC1\d{2}(\d{4})\d{8}", t):
        city = code_city.get(m.group(1))
        mm = re.search(r"(?:生产商|受委托生产企业|生产企业)：([^」]+)", t)
        if city and mm:
            cn = city.replace("市", "").replace("回族自治州", "")
            if cn not in mm.group(1) and "manufacturer_info_tamper" not in r["tamper_types"]:
                hit("sc_region_vs_company_city", r)
        elif not city:
            hit("sc_region_unknown", r)
    # selling copy / visual keywords not in ingredients (food only)
    if r["super_category"] in ("食品标签", "商业广告") and il:
        vis = re.search(r"(?:包装外观|商品外观)：([^；。\n]+)", p)
        if vis and kw_missing(vis.group(1), [il]):
            hit("visual_kw_not_in_ing", r)
        if vis and has_place(vis.group(1)):
            hit("visual_place", r)
        if "素" in r["product_or_title"] and any(a in il for a in ["牛油", "猪", "牛肉", "鸡肉"]):
            hit("veg_name_animal", r)
    # NRV rounding half-up in clean
    if r["variant"] == "clean":
        for m in re.finditer(r"「([^｜」]+)｜([\d.]+) (kJ|g|mg)｜(\d+)%」", p):
            nrv = {"能量": 8400, "蛋白质": 60, "脂肪": 60, "碳水化合物": 300, "钠": 2000, "膳食纤维": 25, "钙": 800}.get(m.group(1))
            if nrv:
                import math
                e = int(math.floor(round(float(m.group(2)) / nrv * 100, 6) + 0.5))
                if e != int(m.group(4)):
                    hit("clean_nrv_halfup", r)
        cm = re.search(r"「碳水化合物｜([\d.]+) g", p)
        if cm and float(cm.group(1)) > 100:
            hit("carb_over_100", r)
        sm = re.search(r"「—饱和脂肪｜([\d.]+) g", p)
        fm = re.search(r"「脂肪｜([\d.]+) g", p)
        if sm and fm and float(sm.group(1)) > float(fm.group(1)):
            hit("sat_gt_fat", r)
        if "氢化" in il and "反式脂肪" not in p:
            hit("hydrogenated_no_trans", r)
    # multi-pack spec on single-unit carriers
    if r["carrier"] in ("bottle", "can", "carton") and re.search(r"净含量[^」]*×\d+(瓶|罐|盒)", t):
        hit("multipack_on_unit_label", r)
    # numeric nutrient in selling copy
    if re.search(r"「[^」]*\d+(\.\d+)?\s*(g|克)\s*(优质)?蛋白", p):
        hit("numeric_protein_claim", r)
    # 8-digit phone for 7-digit city
    for m in re.finditer(r"(0\d{2,3})-(\d{7,8})(?!\d)", t):
        if len(m.group(2)) == 8 and m.group(1) not in B.EIGHT_DIGIT:
            hit("phone_8_digits_small_city", r)
    # style vs palette double colour spec
    if r["super_category"] in ("公益海报", "活动宣传") and "配色：" in head and re.search(r"视觉风格：[^；]*(色|配色)", head):
        hit("double_colour_spec", r)
    if "10^" in p:
        hit("caret_notation", r)
    if "圆角标签：无" in p:
        hit("literal_wu_tag", r)
    if "八类致敏物质" in t and r["variant"] == "clean":
        sec = re.search(r"小标题「八类致敏物质」】要点逐条[^：]*：(.+?)。\n", p)
        if sec and "坚果" not in sec.group(1):
            hit("eight_allergen_incomplete", r)
    if r["super_category"] == "公益海报" and "地铁" in head:
        if not any(c in t for c in ["上海市", "天津市", "重庆市", "长沙市", "沈阳市", "长春市", "南宁市", "佛山市", "石家庄市", "南通市", "呼和浩特市", "嘉兴市"]):
            hit("metro_city", r)
print(json.dumps(C, ensure_ascii=False, indent=1))
print(json.dumps(ex, ensure_ascii=False))
