"""Food product spec builder + tamper operators (shared by food_label and commercial_ad scenes)."""
import copy
import re
from common import (rng_for, add_days, add_months, expiry_of, fmt_date, shelf_str, build_nutrition,
                    nutrition_rows, nrv_pct, fmt_num, unit_of, money, money_short, NUT_NAME)
import brands as B
from consistency import kw_missing, container_class, ean13 as _ean13, GS1, FOREIGN_MFR, serving_pack_ok, name_conflict, has_place, nutrient_mention_ok

ALLERGEN_WORD = {"麸质": None, "甲壳": "虾", "鱼": "鱼", "蛋": "鸡蛋", "花生": "花生", "大豆": "大豆", "乳": "乳", "坚果": None}
GRAINS = ["小麦", "大麦", "燕麦", "黑麦", "荞麦"]
NUTS = ["杏仁", "腰果", "榛子", "核桃", "开心果", "巴旦木", "碧根果", "夏威夷果", "松子", "山核桃"]
SHRIMP = ["虾", "蟹", "龙虾"]


SOY_EXEMPT = ("精炼大豆油", "大豆油")
IMPORT_ORIGINS_BY_CAT = {"乳制品": ["新西兰", "澳大利亚", "丹麦", "德国"], "饮料": ["泰国", "越南", "马来西亚", "韩国", "日本"],
                         "零食": ["泰国", "马来西亚", "韩国", "日本", "越南"], "烘焙": ["日本", "韩国", "马来西亚", "德国", "比利时"],
                         "蜂产品糖果": ["新西兰", "澳大利亚", "德国", "比利时", "日本"], "冲调谷物": ["澳大利亚", "德国", "马来西亚"],
                         "儿童食品": ["日本", "韩国"]}


def allergen_words(ings):
    """ingredient list (dicts) -> ordered list of allergen display words (specific where possible).
    Dataset convention: 大豆磷脂 is declared as soy even though GB 7718-2025 D.4 allows 磷脂 exemption (conservative labelling
    practice; avoids clean labels that look incomplete)."""
    VIS = {"麸质": ["麦", "面", "麸", "酱油", "豆瓣", "酱"], "乳": ["乳", "奶", "黄油", "芝士", "干酪", "酪", "稀奶油"], "蛋": ["蛋"],
           "大豆": ["大豆", "豆粉", "黄豆", "酱油", "豆瓣", "豆豉", "磷脂", "豆浆", "腐竹", "豆腐", "味噌"],
           "花生": ["花生"], "鱼": ["鱼"], "甲壳": ["虾", "蟹"], "坚果": NUTS + ["坚果", "仁"]}
    out = []
    for x in ings:
        tags = [a for a in x.get("a", []) if any(w in x["n"] for w in VIS.get(a, [a]))]
        if "大豆磷脂" in x["n"] and "大豆" not in tags:
            tags.append("大豆")
        if "花生" in x["n"] and "花生" not in tags:
            tags.append("花生")
        if any(w in x["n"] for w in ("黑豆", "青豆", "毛豆", "腐竹")) and "大豆" not in tags:
            tags.append("大豆")
        for a in tags:
            if a == "麸质":
                w = next((g for g in GRAINS if g in x["n"]), None) or ("小麦" if "麦" in x["n"] or "面" in x["n"] else "小麦")
            elif a == "坚果":
                w = next((n for n in NUTS if n in x["n"]), None) or "坚果"
            elif a == "甲壳":
                w = next((s for s in SHRIMP if s in x["n"]), None) or "虾"
            elif a == "大豆":
                w = "大豆"
            elif a == "乳":
                w = "乳"
            else:
                w = ALLERGEN_WORD[a]
            if (a, w) not in [(o[0], o[1]) for o in out]:
                out.append((a, w))
    return out


def allergen_text(pairs, style):
    words = []
    for a, w in pairs:
        if a == "乳":
            words.append("乳制品" if style != 2 else "乳成分")
        elif a == "大豆":
            words.append("大豆制品" if style != 2 else "大豆")
        elif a == "麸质":
            words.append(f"{w}（含麸质谷物）" if style == 1 else w)
        else:
            words.append(w)
    lead = ["过敏原信息：本产品含有", "致敏物质提示：含有", "食物过敏原提示：本产品含有"][style % 3]
    return lead + "、".join(words) + "。"


def ean13(rng, prefix="69"):
    return _ean13(rng, prefix)


def price_round(x):
    """Chinese retail price endings."""
    if x < 10:
        return round(int(x) + 0.9, 2)
    base = int(x)
    return float(f"{base}.9") if base % 10 != 9 else float(f"{base}.9")


BRAND_CODE_CH = "ABDEFGHJKLMNPQRTWXYZ"  # no C/S so a batch never starts with "SC"


def batch_code(rng, d, style, prefix):
    yymmdd = d.strftime("%y%m%d")
    line = rng.choice("ABCDEFGH")
    seq = rng.randint(1, 12)
    if style == 0:
        return f"{prefix}{yymmdd}{line}{seq:02d}", ("批号", )
    if style == 1:
        return f"{d.strftime('%Y%m%d')}{line}{seq:02d}", ("生产批号", )
    if style == 2:
        return f"{yymmdd}{line}{seq:02d}", ("LOT", )
    return f"{d.strftime('%Y-%m-%d')}-{seq:02d}", ("生产批次", )


def recode_batch(code, old, new):
    for f in ("%y%m%d", "%Y%m%d", "%Y-%m-%d"):
        o, n = old.strftime(f), new.strftime(f)
        if o in code:
            return code.replace(o, n)
    return code


def fictional_standard(rng, brand_abbr):
    return f"Q/{brand_abbr} {rng.randint(1, 60):04d}S-{rng.choice([2023, 2024, 2025])}"


CLAIM_RULES = {  # GB 28050-2011 Table C.1 (subset). (key, solid_limit, liquid_limit, op)
    "低脂": ("fat", 3, 1.5, "<="), "脱脂": ("fat", 0.5, 0.5, "<="), "0脂肪": ("fat", 0.5, 0.5, "<="), "无脂肪": ("fat", 0.5, 0.5, "<="),
    "无糖": ("sugar", 0.5, 0.5, "<="), "0糖": ("sugar", 0.5, 0.5, "<="), "低糖": ("sugar", 5, 5, "<="), "不含糖": ("sugar", 0.5, 0.5, "<="),
    "高蛋白": ("protein", 12, 6, ">="), "富含蛋白质": ("protein", 12, 6, ">="), "蛋白质来源": ("protein", 6, 3, ">="),
    "高膳食纤维": ("fiber", 6, 3, ">="), "富含膳食纤维": ("fiber", 6, 3, ">="), "膳食纤维来源": ("fiber", 3, 1.5, ">="),
    "低钠": ("sodium", 120, 120, "<="), "低盐": ("sodium", 120, 120, "<="), "高钙": ("calcium", 240, 120, ">="),
    "钙来源": ("calcium", 120, 60, ">="), "高维生素C": ("vitc", 30, 15, ">="), "低能量": ("energy", 170, 80, "<="),
    "0反式脂肪酸": ("trans", 0.3, 0.3, "<="), "零乳糖": ("lactose", 0.5, 0.5, "<="), "无乳糖": ("lactose", 0.5, 0.5, "<="),
    "低乳糖": ("lactose", 2, 2, "<="),
}


def per100(spec, k):
    v = spec["nut_shown"].get(k)
    if v is None:
        return None
    if spec["basis"] == "serving":
        return v * 100 / spec["serving"]["size"]
    return v


def claim_holds(spec, claim):
    r = CLAIM_RULES.get(claim)
    if not r:
        return True
    k, sl, ll, op = r
    v = per100(spec, k)
    if v is None:
        return False
    liquid = ("mL" in spec["basis_label"]) if spec["basis"] != "serving" else spec["form"] == "liquid"
    lim = ll if liquid else sl
    return v <= lim if op == "<=" else v >= lim


def claim_fails(spec, claim):
    r = CLAIM_RULES.get(claim)
    if not r:
        return False
    k = r[0]
    return spec["nut_shown"].get(k) is not None and not claim_holds(spec, claim)


FUNC_NEEDS = [("钙", ["高钙", "钙来源"]), ("蛋白质", ["高蛋白", "富含蛋白质", "蛋白质来源"]),
              ("膳食纤维", ["高膳食纤维", "富含膳食纤维", "膳食纤维来源"]), ("维生素C", ["高维生素C"]),
              ("脂肪", ["低脂", "脱脂", "0脂肪", "无脂肪"]), ("钠", ["低钠", "低盐"])]


def pick_price(rng, lo, hi):
    return price_round(rng.uniform(lo, hi))


def make_food_spec(arc, gid, brand, ref, festival=None, imported=False, pack_pref=None, pack_filter=None, unit_label=False):
    """ref: dict with 'start' (date) = earliest date the image is 'shown' (promo start / photo date)."""
    rng = rng_for("food", gid)
    spec = {"arc_id": arc["id"], "sub_category": arc["sub_category"], "product_type": arc["product_type"],
            "form": arc["form"], "brand": brand, "imported": imported}
    # name + recipe: only (name, recipe) pairs whose name keywords are backed by that recipe's ingredients
    pairs = [(ni, ri) for ri, r in enumerate(arc["recipes"]) for ni in r.get("names", range(len(arc["names"])))
             if not kw_missing(arc["names"][ni], [x["n"] for x in r["ing"]]) and not name_conflict(arc["names"][ni], [x["n"] for x in r["ing"]])]
    if not pairs:
        pairs = [(ni, ri) for ri, r in enumerate(arc["recipes"]) for ni in r.get("names", range(len(arc["names"])))]
    ni, ri = rng.choice(pairs)
    rec = copy.deepcopy(arc["recipes"][ri])
    spec["name_core"] = arc["names"][ni]
    spec["name"] = f"{brand} {arc['names'][ni]}"
    pks = arc["packages"]
    if pack_filter:
        pks = [p for p in pks if pack_filter(p)] or pks
    vis_c = container_class(arc["visual"])
    m_ = [p for p in pks if container_class(p["pack"]) == vis_c]
    pks = m_ or pks
    if arc["basis"] == "serving":
        pks = [p for p in pks if serving_pack_ok(p["net"], arc["serving"]["size"])] or pks
    pk = copy.deepcopy(rng.choice(pks))
    # packaging look must describe the chosen container: when it does not, describe it from the pack field instead
    spec["visual_override"] = None
    if vis_c and container_class(pk["pack"]) not in (None, vis_c):
        spec["visual_override"] = f"{pk['pack']}包装，" + re.split("[，,]", arc["visual"], 1)[-1]
    spec["pack"] = pk
    spec["net"] = pk["net"]
    spec["count"] = pk.get("count", 1)
    spec["unit_word"] = pk.get("unit_word", "袋")
    spec["net_text"] = pk["net"] if spec["count"] == 1 else f"{pk['net']}×{spec['count']}{spec['unit_word']}"
    if unit_label and spec["count"] > 1:   # a single bottle/can/carton label carries the unit's own net content
        spec["count"] = 1
        spec["net_text"] = pk["net"]
        spec["price_scale_single"] = True
    m = re.match(r"([\d.]+)\s*(mL|ml|L|g|kg|克|毫升)", pk["net"])
    spec["net_num"] = float(m.group(1)) if m else None
    spec["net_unit"] = m.group(2) if m else ""
    spec["price_orig"] = pick_price(rng, *pk["price"])
    # ingredients
    ings = sorted(rec["ing"], key=lambda x: -x["p"])
    spec["ing_objs"] = ings
    spec["ingredients"] = [x["n"] for x in ings]
    spec["ingredients_true"] = list(spec["ingredients"])
    spec["hero"] = [x["n"] for x in ings if x.get("hero")]
    spec["allergen_pairs"] = allergen_words(ings)
    spec["allergen_style"] = rng.randrange(3)
    present = {a for a, _ in spec["allergen_pairs"]}
    mc = [w for w in ["花生", "坚果", "大豆", "乳", "小麦", "鸡蛋"] if not ({"花生": "花生", "坚果": "坚果", "大豆": "大豆", "乳": "乳",
                                                                  "小麦": "麸质", "鸡蛋": "蛋"}[w] in present)]
    spec["may_contain"] = (f"本生产线还加工含有{'、'.join(rng.sample(mc, 2))}的产品。" if mc and len(mc) >= 2 and rng.random() < 0.45 else None)
    spec["allergen_statement"] = allergen_text(spec["allergen_pairs"], spec["allergen_style"]) if spec["allergen_pairs"] else None
    spec["allergen_free_claim"] = None
    # nutrition
    spec["basis"] = arc["basis"]
    spec["serving"] = arc.get("serving")
    keys = [k for k in arc["nut_keys"] if k in ("energy", "protein", "fat", "carb", "sodium") or rec["nut"].get(k)]
    if rec["nut"].get("calcium") and "calcium" not in keys and any(("钙" in x["n"] and x["p"] >= 0.1) for x in ings):
        keys.append("calcium")
    if any("氢化" in x["n"] for x in ings) and "trans" not in keys:  # GB 28050: hydrogenated oil -> trans fat must be declared
        keys.insert(keys.index("fat") + 1, "trans")
        rec["nut"].setdefault("trans", 0.4 + 0.1 * (len(ings) % 5))
    spec["nut_keys"] = keys
    scale = 1.0
    if arc["basis"] == "serving":
        scale = arc["serving"]["size"] / 100.0
    spec["nut_shown"] = build_nutrition(rec["nut"], keys, rng, jitter=0.07, scale=scale, solid=(arc["form"] == "solid"))
    spec["nut_nrv_override"] = {}
    spec["nut_unit_override"] = {}
    if arc["basis"] == "serving":
        spec["basis_label"] = arc["serving"].get("label") or f"每份（{arc['serving']['size']}{arc['serving']['unit']}）"
    else:
        spec["basis_label"] = "每100mL" if arc["basis"] == "100mL" else "每100g"
    # claims
    spec["claims"] = [c for c in arc["claims_ok"] if claim_holds(spec, c)]
    for strong_c, weak_c in [("高钙", "钙来源"), ("高蛋白", "蛋白质来源"), ("富含蛋白质", "蛋白质来源"), ("高膳食纤维", "膳食纤维来源"),
                             ("富含膳食纤维", "膳食纤维来源"), ("无糖", "低糖"), ("0糖", "低糖"), ("脱脂", "低脂")]:
        if strong_c in spec["claims"] and weak_c in spec["claims"]:
            spec["claims"].remove(weak_c)
    fc = arc.get("function_claim")
    if fc:
        ok = False
        for kw, need in FUNC_NEEDS:
            if kw in fc:
                ok = any(c in spec["claims"][:3] for c in need)
                break
        spec["function_claim"] = fc if ok else None
    else:
        spec["function_claim"] = None
    ingn = [x["n"] for x in ings]
    ok = lambda t: not kw_missing(t, ingn) and not has_place(t) and nutrient_mention_ok(t, keys) and not name_conflict(t, ingn)
    sel = [x for x in arc["selling"] if ok(x)] or [arc["selling"][0]]
    rng.shuffle(sel)
    spec["selling"] = sel[:3]
    spec["exag_subtle"] = [x for x in arc["exag_subtle"] if ok(x)] or arc["exag_subtle"]
    spec["exag_strong"] = [x for x in arc["exag_strong"] if ok(x)] or arc["exag_strong"]
    # the product name must not carry a nutrient claim the table does not support (e.g. “低脂” in the name, 6.3 g fat)
    for c in sorted(CLAIM_RULES, key=len, reverse=True):
        if c in spec["name_core"] and claim_fails(spec, c):
            spec["name_core"] = spec["name_core"].replace(c, "")
            spec["name"] = f"{brand} {spec['name_core']}"
    spec["headline_extra"] = []
    # dates
    sv, su = arc["shelf"]
    spec["shelf"] = [sv, su]
    spec["shelf_tamper"] = arc["shelf_tamper"]
    start = ref["start"]
    if su == "天":
        back = rng.randint(1, max(2, min(int(sv * 0.25), 20)))
    else:
        months = sv
        back = rng.randint(4, max(6, min(int(months * 30 * 0.25), 75)))
    prod = add_days(start, -back)
    spec["prod_date"] = prod
    spec["prod_date_true"] = prod
    spec["expiry"] = expiry_of(prod, sv, su)
    spec["date_style"] = rng.choice(["cn0", "iso", "dot", "cn0"])
    # batch
    abbr = "".join(rng.choice(BRAND_CODE_CH) for _ in range(2))
    spec["brand_abbr"] = abbr
    bstyle = rng.randrange(4)
    code, (lab,) = batch_code(rng, prod, bstyle, abbr)
    spec["batch"] = code
    spec["batch_label"] = lab
    spec["batch_true"] = code
    spec["inkjet"] = None
    # standard
    st = arc.get("standard")
    if imported:
        spec["standard"] = None
        spec["standard_real"] = False
    elif st and st.get("verified"):
        spec["standard"] = st["code"]
        spec["standard_real"] = True
    else:
        spec["standard"] = fictional_standard(rng, abbr + rng.choice(BRAND_CODE_CH))
        spec["standard_real"] = False
    spec["wrong_standard"] = arc.get("wrong_standard")
    spec["standard2"] = None
    # company
    co = B.company_cat(rng, arc["sub_category"])
    spec["manufacturer"] = co
    spec["entrust"] = None
    if not imported and rng.random() < 0.3:
        owner = B.company_cat(rng, arc["sub_category"])
        owner["name"] = owner["name"].replace("乳业有限公司", "食品科技有限公司").replace("饮品有限公司", "品牌管理有限公司")
        spec["entrust"] = owner
    spec["mfr_addr_shown2"] = None
    spec["origin"] = co["addr"]["city"]
    spec["origin_shown"] = None
    spec["license"] = B.sc_license_city(rng, B.sc_cat_for(arc), co["addr"]["city"]) if not imported else None
    spec["phone"] = B.phone400(rng)
    spec["storage"] = arc["storage"]
    spec["storage_tamper"] = arc.get("storage_tamper")
    spec["usage"] = arc.get("usage")
    spec["population"] = arc.get("population")
    spec["attr_tamper"] = arc.get("attr_tamper")
    spec["attr_text"] = None
    spec["ean"] = ean13(rng)
    vis = spec["visual_override"] or arc["visual"]
    segs = re.split("([，、])", vis)
    keep = [segs[0]] + [segs[i] + segs[i + 1] for i in range(1, len(segs) - 1, 2) if not kw_missing(segs[i + 1], ingn) and not has_place(segs[i + 1])]
    spec["visual"] = "".join(keep).strip("，、")
    spec["digital_label"] = rng.random() < 0.35
    spec["net_shown2"] = None
    spec["count_shown2"] = None
    spec["quant_note"] = None
    spec["hero_pct_line"] = None
    spec["extra_label_lines"] = []
    if arc["id"] == "oil_blended":
        oils = [x for x in ings if "油" in x["n"]]
        spec["extra_label_lines"].append("调和比例：" + "、".join(f"{x['n']}{int(round(x['p']))}%" for x in oils))
    # hero percentage (定量标示) – sometimes present in clean (true value) for realism
    heros = [x for x in ings if x.get("hero")]
    named = [h for h in heros if any(k in spec["name_core"] for k in re.findall(r"[\u4e00-\u9fa5]{2}", h["n"]))]
    if len(ings) >= 3 and named and named[0]["p"] < 60:
        h = named[0]
        spec["hero_pct_line"] = f"{h['n']}添加量≥{max(1, int(h['p']))}%"
    elif heros and len(ings) >= 3 and heros[0]["p"] < 60 and rng.random() < 0.35:
        h = heros[0]
        spec["hero_pct_line"] = f"{h['n']}添加量≥{max(1, int(h['p']))}%"
    if imported:
        spec["import_info"] = {
            "origin_country": rng.choice(IMPORT_ORIGINS_BY_CAT.get(arc["sub_category"], ["日本", "韩国"])),
            "importer": B.company(rng, "food")["name"].replace("食品有限公司", "进出口贸易有限公司").replace("食品股份有限公司", "国际贸易有限公司")
            .replace("乳业有限公司", "进出口有限公司").replace("饮品有限公司", "贸易有限公司").replace("食品科技有限公司", "供应链管理有限公司")
            .replace("农业发展有限公司", "进出口有限公司"),
            "importer_addr": B.address(rng)["text"],
        }
        spec["import_info"]["foreign_mfr"] = FOREIGN_MFR[spec["import_info"]["origin_country"]]
        imp_addr = B.address(rng)
        spec["import_info"]["importer_addr"] = imp_addr["text"]
        spec["import_info"]["importer"] = f"{imp_addr['city'].replace('市', '').replace('回族自治州', '')}{rng.choice(B.ZIHAO)}{rng.choice(['进出口贸易有限公司', '国际贸易有限公司', '供应链管理有限公司'])}"
        spec["ean"] = ean13(rng, GS1[spec["import_info"]["origin_country"]])
    else:
        spec["import_info"] = None
    return spec


# ---------------------------------------------------------------- text helpers
def d(spec, dt_):
    return fmt_date(dt_, spec["date_style"])


def ingredients_line(spec):
    return "配料：" + "、".join(spec["ingredients"]) + "。"


def nutrition_table_text(spec):
    rows = nutrition_rows(spec["nut_shown"], spec["nut_keys"])
    lines = []
    for r in rows:
        k = r["key"]
        unit = spec["nut_unit_override"].get(k, r["unit"])
        nrv = spec["nut_nrv_override"].get(k, r["nrv"])
        lines.append(f"{r['name']}｜{fmt_num(k, r['value'])} {unit}｜{nrv}")
    return lines


def dates_lines(spec):
    sv, su = spec["shelf"]
    return [f"生产日期：{d(spec, spec['prod_date'])}", f"保质期：{shelf_str(sv, su)}",
            f"保质期至：{d(spec, spec['expiry'])}"]


def batch_line(spec):
    sep = "：" if spec["batch_label"] != "LOT" else "："
    return f"{spec['batch_label']}{sep}{spec['batch']}"


def standard_lines(spec):
    out = []
    if spec["standard"]:
        out.append(f"产品标准代号：{spec['standard']}")
    if spec["standard2"]:
        out.append(f"执行标准：{spec['standard2']}")
    return out


def producer_lines(spec):
    m = spec["manufacturer"]
    out = []
    if spec["import_info"]:
        ii = spec["import_info"]
        out.append(f"原产国：{ii['origin_country']}")
        out.append(f"生产商：{ii['foreign_mfr']}")
        out.append(f"进口商/经销商：{ii['importer']}")
        out.append(f"地址：{ii['importer_addr']}")
        out.append(f"联系电话：{spec['phone']}")
        return out
    if spec["entrust"]:
        e = spec["entrust"]
        out.append(f"委托方：{e['name']}")
        out.append(f"委托方地址：{e['addr']['text']}")
        out.append(f"受委托生产企业：{m['name']}")
        out.append(f"生产地址：{spec['mfr_addr_shown2'] or m['addr']['text']}")
    else:
        out.append(f"生产商：{m['name']}")
        out.append(f"地址：{spec['mfr_addr_shown2'] or m['addr']['text']}")
    out.append(f"产地：{spec['origin_shown'] or spec['origin']}")
    if spec["license"]:
        out.append(f"食品生产许可证编号：{spec['license']}")
    out.append(f"服务热线：{spec['phone']}")
    return out


def claims_display(spec):
    return list(spec["claims"])


# ---------------------------------------------------------------- tamper operators
# Each op: fn(spec, level, rng, ctx) -> dict(type, field, detail) or None if not applicable.
def _t(type_, field, detail):
    return {"type": type_, "field": field, "detail": detail}


def op_efficacy(spec, level, rng, ctx):
    if level == "subtle":
        line = rng.choice(spec["exag_subtle"])
        old = spec["selling"][0] if spec["selling"] else None
        if spec["selling"]:
            spec["selling"][0] = line
        else:
            spec["selling"] = [line]
        return _t("efficacy_exaggeration", "selling_claim", f"卖点文案「{old}」被替换为轻度夸大功效表述「{line}」")
    lines = rng.sample(spec["exag_strong"], min(2, len(spec["exag_strong"])))
    spec["headline_extra"] = lines
    if spec["selling"]:
        spec["selling"][0] = lines[0]
    return _t("efficacy_exaggeration", "headline_claim", f"加入明显越界的医疗化/绝对化功效声明：{'；'.join('「'+x+'」' for x in lines)}")


def op_allergen(spec, level, rng, ctx):
    pairs = spec["allergen_pairs"]
    if not pairs or len(spec["ingredients"]) <= 1:
        return None
    if level == "subtle":
        if len(pairs) >= 2:
            i = rng.randrange(len(pairs))
            removed = pairs[i]
            spec["allergen_pairs"] = pairs[:i] + pairs[i + 1:]
            spec["allergen_statement"] = allergen_text(spec["allergen_pairs"], spec["allergen_style"])
            return _t("allergen_deletion", "allergen_statement", f"过敏原提示中删除了「{removed[1]}」，但配料表仍含对应配料")
        # single allergen: delete statement quietly
        spec["allergen_statement"] = None
        return _t("allergen_deletion", "allergen_statement", f"唯一的过敏原提示（{pairs[0][1]}）被整句删除，配料表仍含对应配料")
    spec["allergen_statement"] = None
    spec["may_contain"] = None
    free = [w for _, w in pairs if w not in spec["name_core"] and w not in ("乳",) or (w == "乳" and not any(x in spec["name_core"] for x in "奶乳酪"))]
    opts = ["0过敏原配方 敏感人群安心食用", "无致敏原 敏感体质也能放心吃"]
    if free:
        w = free[0]
        opts.append(f"不含{w if w != '乳' else '乳制品'} · 敏感人群安心食用")
    txt = rng.choice(opts)
    spec["allergen_free_claim"] = txt
    return _t("allergen_deletion", "allergen_statement+front_claim",
              f"完全删除过敏原提示，并在正面加入与配料冲突的「{txt}」")


def op_prod_date(spec, level, rng, ctx):
    old = spec["prod_date"]
    if level == "subtle":
        delta = rng.choice([-9, -6, -4, -3, 3, 4, 5, 7, 10])
        new = add_days(old, delta)
        if new >= ctx["ref_start"]:
            new = add_days(old, -abs(delta))
        spec["prod_date"] = new
        spec["expiry"] = expiry_of(new, *spec["shelf"]) if spec["shelf"][1] != "小时" else new
        return _t("production_date_tamper", "production_date",
                  f"生产日期由{fmt_date(old,'iso')}改为{fmt_date(new,'iso')}（保质期至同步推算），但批号「{spec['batch']}」仍对应原生产日期")
    # strong
    if spec.get("inkjet_enabled"):
        sv, su = spec["shelf"]
        span = 150 if su == "月" else max(3, int(sv * 0.6))
        new = add_days(old, span)
        cap = add_days(ctx["ref_start"], -1)
        if new > cap:
            new = cap if cap > add_days(old, 2) else add_days(old, 3)
        spec["prod_date"] = new
        spec["expiry"] = expiry_of(new, sv, su)
        spec["batch"] = recode_batch(spec["batch"], old, new)
        return _t("production_date_tamper", "production_date+batch",
                  f"标签印刷的生产日期被整体改晚为{fmt_date(new,'iso')}（批号、保质期至一并改写），但喷码区仍保留原始生产日期{fmt_date(old,'iso')}与原批号，属临期产品改标")
    new = add_days(ctx["ref_start"], rng.randint(4, 15))
    spec["prod_date"] = new
    spec["expiry"] = expiry_of(new, *spec["shelf"])
    return _t("production_date_tamper", "production_date",
              f"生产日期被改为{fmt_date(new,'iso')}，晚于画面中的活动/展示起始日{fmt_date(ctx['ref_start'],'iso')}，且与批号「{spec['batch']}」不符")


def op_shelf(spec, level, rng, ctx):
    sv, su = spec["shelf"]
    tv, tu = spec["shelf_tamper"]
    if level == "subtle":
        if rng.random() < 0.5:
            spec["shelf"] = [tv, tu]
            return _t("shelf_life_tamper", "shelf_life",
                      f"保质期由{shelf_str(sv,su)}改为{shelf_str(tv,tu)}，而「保质期至」日期仍按原{shelf_str(sv,su)}推算，二者不一致")
        old = spec["expiry"]
        new = add_months(old, rng.choice([1, 2, 3])) if su == "月" else add_days(old, max(2, int(sv * 0.4)))
        spec["expiry"] = new
        return _t("shelf_life_tamper", "expiry_date",
                  f"「保质期至」由{fmt_date(old,'iso')}延后为{fmt_date(new,'iso')}，与生产日期+保质期{shelf_str(sv,su)}不符")
    spec["shelf"] = [tv, tu]
    old = spec["expiry"]
    spec["expiry"] = expiry_of(spec["prod_date"], tv, tu)
    extra = ""
    # keep a visible cue: the inkjet/secondary print keeps the ORIGINAL expiry
    spec["expiry_ink"] = old
    if spec.get("storage_tamper"):
        spec["storage"] = spec["storage_tamper"]
        extra = f"，贮存条件同时被改为「{spec['storage_tamper']}」"
    return _t("shelf_life_tamper", "shelf_life+expiry",
              f"保质期由{shelf_str(sv,su)}延长为{shelf_str(tv,tu)}，印刷的保质期至由{fmt_date(old,'iso')}改为{fmt_date(spec['expiry'],'iso')}，"
              f"而喷码区仍保留原保质期至{fmt_date(old,'iso')}{extra}")


def op_ing_order(spec, level, rng, ctx):
    ings = spec["ingredients"]
    heros = [h for h in spec["hero"] if h in ings]
    if not heros:
        return None
    idx = {n: i for i, n in enumerate(ings)}
    movable = [h for h in heros if idx[h] > 0]
    if not movable:
        return None
    if level == "subtle":
        h = min(movable, key=lambda x: idx[x])
        i = idx[h]
        j = max(0, i - rng.choice([1, 2])) if i > 1 else 0
        new = ings[:j] + [h] + [x for x in ings[j:] if x != h]
        spec["ingredients"] = new
        return _t("ingredient_order_tamper", "ingredients",
                  f"配料「{h}」被从第{i+1}位前移到第{j+1}位（真实加入量排序中它应排在「{ings[j]}」之后）")
    hs = sorted(movable, key=lambda x: idx[x])
    if len(ings) < 3:
        return None
    new = hs + [x for x in ings if x not in hs]
    spec["ingredients"] = new
    true_first = ings[0]
    h0 = next(x for x in spec["ing_objs"] if x["n"] == hs[0])
    spec["hero_pct_line"] = f"{h0['n']}添加量≥{max(1, int(h0['p']))}%"
    return _t("ingredient_order_tamper", "ingredients",
              f"「{'、'.join(hs)}」被整体提到配料表最前，真实首位配料「{true_first}」被后移；同时标示{h0['n']}添加量≥{max(1,int(h0['p']))}%，与其位列首位相矛盾")


def op_nutrition(spec, level, rng, ctx):
    keys = [k for k in ["sodium", "fat", "sugar", "protein", "carb", "calcium", "fiber"] if k in spec["nut_shown"] and spec["nut_shown"][k]]
    if not keys:
        return None
    if level == "subtle":
        k = rng.choice(keys)
        v = spec["nut_shown"][k]
        orig_pct = nrv_pct(k, v)
        mode = rng.random()
        if mode < 0.55 and orig_pct is not None:
            if k in ("sodium", "calcium"):
                nv = int(v * rng.choice([0.62, 0.7, 1.35]))
            else:
                nv = round(v * rng.choice([0.6, 0.7, 1.4]), 1)
            spec["nut_shown"][k] = nv
            spec["nut_nrv_override"][k] = f"{orig_pct}%"
            return _t("nutrition_value_tamper", f"nutrition.{k}",
                      f"营养成分表中{NUT_NAME[k].lstrip('—')}数值由{fmt_num(k,v)}改为{fmt_num(k,nv)}，NRV%仍保留原值{orig_pct}%，二者不匹配")
        if k in ("sodium", "calcium"):
            spec["nut_unit_override"][k] = "g"
            return _t("nutrition_value_tamper", f"nutrition.{k}.unit",
                      f"{NUT_NAME[k]}单位由mg改为g（{fmt_num(k,v)} g），数量级错误")
        spec["nut_unit_override"][k] = "mg"
        return _t("nutrition_value_tamper", f"nutrition.{k}.unit", f"{NUT_NAME[k].lstrip('—')}单位由g改为mg，数量级错误")
    # strong: lower fat/sugar/sodium massively and raise protein; energy left unchanged -> inconsistent
    changed = []
    for k in ["fat", "sugar", "sodium", "sat"]:
        if k in spec["nut_shown"] and spec["nut_shown"][k]:
            v = spec["nut_shown"][k]
            p0 = nrv_pct(k, v)
            nv = int(v * 0.3) if k == "sodium" else round(v * 0.3, 1)
            spec["nut_shown"][k] = nv
            if p0 is not None:
                spec["nut_nrv_override"][k] = f"{p0}%"
            if k == "sat":
                continue
            changed.append(f"{NUT_NAME[k].lstrip('—')}{fmt_num(k,v)}→{fmt_num(k,nv)}")
    if "protein" in spec["nut_shown"]:
        v = spec["nut_shown"]["protein"]
        spec["nut_nrv_override"]["protein"] = f"{nrv_pct('protein', v)}%"
        nv = round(v * 2.2 + 1, 1)
        spec["nut_shown"]["protein"] = nv
        changed.append(f"蛋白质{fmt_num('protein',v)}→{fmt_num('protein',nv)}")
    return _t("nutrition_value_tamper", "nutrition_table",
              f"营养成分表多项数值被改写（{'，'.join(changed)}），能量与NRV%未随之变化，能量与三大营养素不再自洽")


CONFLICT_TPL = {
    "sugar": [("低糖", "0糖"), ("低糖", "无糖")],
    "fat": [("低脂", "0脂肪")],
    "protein": [("蛋白质来源", "高蛋白")],
    "sodium": [("低钠", "0钠")],
    "fiber": [("膳食纤维来源", "高膳食纤维")],
    "calcium": [("钙来源", "高钙")],
}


def op_claim_conflict(spec, level, rng, ctx):
    cands = []
    for k, pairs in CONFLICT_TPL.items():
        if k not in spec["nut_shown"]:
            continue
        for sub, strong in pairs:
            c = sub if level == "subtle" else strong
            if claim_fails(spec, c) and c not in spec["claims"]:
                cands.append((k, c))
    # special subtle: 低糖 -> 无糖 when 低糖 legit
    if level == "subtle" and "低糖" in spec["claims"] and claim_fails(spec, "无糖"):
        cands.append(("sugar", "无糖*"))
    if not cands:
        return None
    k, c = rng.choice(cands)
    if c == "无糖*":
        spec["claims"] = ["无糖" if x == "低糖" else x for x in spec["claims"]]
        return _t("claim_nutrition_conflict", "nutrient_claim",
                  f"「低糖」被改为「无糖」，但营养成分表中糖为{fmt_num('sugar', spec['nut_shown']['sugar'])} g，超过无糖声称界限")
    spec["claims"] = [c] + spec["claims"]
    return _t("claim_nutrition_conflict", "nutrient_claim",
              f"正面加入「{c}」声称，但营养成分表中{NUT_NAME[k].lstrip('—')}为{fmt_num(k, spec['nut_shown'][k])} {unit_of(k)}（{spec['basis_label']}），不满足该声称条件")


def op_quantity(spec, level, rng, ctx):
    if level == "subtle" or spec["count"] == 1:
        if spec["net_num"]:
            n = spec["net_num"]
            nn = n * rng.choice([1.2, 1.1, 1.25]) if n >= 20 else n + 5
            nn = int(nn) if nn >= 10 else round(nn, 1)
            spec["net_shown2"] = spec["pack"]["net"].replace(str(int(n)) if n == int(n) else str(n), str(nn), 1)
            return _t("quantity_tamper", "net_content",
                      f"正面/宣传区净含量写作「{spec['net_shown2']}」，信息区仍为「{spec['pack']['net']}」，两处不一致")
        return None
    c = spec["count"]
    nc = c + rng.choice([2, 4]) if c >= 4 else c + 1
    spec["count_shown2"] = nc
    return _t("quantity_tamper", "count", f"正面/宣传区写「{nc}{spec['unit_word']}装」，规格信息仍为{spec['net_text']}，件数不一致")


def op_standard(spec, level, rng, ctx):
    s = spec["standard"]
    if not s:
        return None
    if level == "subtle":
        m = re.search(r"(\d{4,5})", s)
        digits = m.group(1)
        pos = rng.randrange(len(digits) - 1)
        nd = list(digits)
        nd[pos], nd[pos + 1] = nd[pos + 1], nd[pos]
        if nd == list(digits):
            nd[pos] = str((int(nd[pos]) + 3) % 10)
        ns = s.replace(digits, "".join(nd), 1)
        spec["standard"] = ns
        return _t("standard_number_tamper", "standard_number", f"标准号数字被局部改动：{s} → {ns}")
    if spec.get("wrong_standard") and spec["standard_real"]:
        spec["standard"] = spec["wrong_standard"]
        return _t("standard_number_tamper", "standard_number", f"标准号被替换为不适用于本品类的{spec['wrong_standard']}（原应为{s}）")
    ns = f"Q/{spec['brand_abbr']}{rng.choice('KMRT')} {rng.randint(61, 99):04d}S-{rng.choice([2019, 2020, 2021])}"
    spec["standard2"] = ns
    return _t("standard_number_tamper", "standard_number", f"同一标签出现两个不同的标准号：{s} 与 {ns}")


def op_batch(spec, level, rng, ctx):
    b = spec["batch"]
    if level == "subtle":
        digs = [i for i, ch in enumerate(b) if ch.isdigit()]
        i = digs[-1]
        nb = b[:i] + str((int(b[i]) + rng.randint(1, 8)) % 10) + b[i + 1:]
        spec["batch2"] = nb
        return _t("batch_number_tamper", "batch_number", f"同一图中两处批号不一致：「{b}」与「{nb}」")
    other = add_days(spec["prod_date"], -rng.randint(40, 120))
    nb = recode_batch(b, spec["prod_date"], other)
    spec["batch"] = nb
    return _t("batch_number_tamper", "batch_number", f"批号被改为「{nb}」，其日期段对应{fmt_date(other,'iso')}，与标示生产日期不符")


def op_manufacturer(spec, level, rng, ctx):
    if spec.get("imported"):
        return None
    m = spec["manufacturer"]
    if level == "subtle":
        a = m["addr"]
        others = [c for c in B.CITIES if c[0] == a["prov"] and c[1] != a["city"]] or [c for c in B.CITIES if c[1] != a["city"]]
        oc = rng.choice(others)[1]
        nt = a["text"].replace(a["city"], oc, 1)
        spec["mfr_addr_shown2"] = nt
        return _t("manufacturer_info_tamper", "manufacturer_address",
                  f"生产地址中的城市被改为「{oc}」（{nt}），与生产商名称及产地「{a['city']}」、区县「{a['district']}」不符")
    alt = B.address(rng)
    for _ in range(50):
        if alt["city"] != m["addr"]["city"] and alt["prov"] != m["addr"]["prov"]:
            break
        alt = B.address(rng)
    spec["origin_shown"] = alt["city"]
    if spec["entrust"]:
        spec["entrust"] = None
        return _t("manufacturer_info_tamper", "manufacturer",
                  f"删除委托/受托关系，仅保留受托厂名称冒充品牌方自产；同时产地改写为「{alt['city']}」，与生产地址所在地不符")
    return _t("manufacturer_info_tamper", "origin", f"产地被写为「{alt['city']}」，与生产商地址所在地「{m['addr']['city']}」不符")


def op_storage(spec, level, rng, ctx):
    if not spec.get("storage_tamper") or spec["storage"] == spec["storage_tamper"]:
        return None
    old = spec["storage"]
    spec["storage"] = spec["storage_tamper"]
    return _t("storage_condition_tamper", "storage", f"贮存条件由「{old}」改为「{spec['storage_tamper']}」，与产品属性不符")


def op_attr(spec, level, rng, ctx):
    t = spec.get("attr_tamper")
    if not t:
        return None
    spec["attr_text"] = t
    return _t("product_attribute_tamper", "product_attribute", f"加入不实的产品属性宣称「{t}」")


def op_population(spec, level, rng, ctx):
    pop = spec.get("population")
    if level == "subtle" and pop and pop not in ("一般人群", None):
        spec["population"] = None
        return _t("target_population_tamper", "population", f"删除了适宜/不适宜人群提示「{pop}」")
    spec["population"] = rng.choice(["老少皆宜，孕妇、婴幼儿、糖尿病人群均可放心食用", "适宜人群：全家老小，特别适合三高人群、孕妇及1岁以上婴幼儿"])
    return _t("target_population_tamper", "population", f"擅自扩大适用人群：「{spec['population']}」")


def op_warning(spec, level, rng, ctx):
    u = spec.get("usage")
    st = spec.get("storage", "")
    if "开启" in st or "开封" in st:
        parts = re.split(r"[，,；;]", st)
        keep = [p for p in parts if "开启" not in p and "开封" not in p and "内饮用" not in p and "内食用" not in p]
        if keep and len(keep) < len(parts):
            spec["storage"] = "，".join(keep).rstrip("。") + "。"
            return _t("warning_deletion", "storage_after_opening", f"删除了开封后保存/食用期限提示（原：「{st}」）")
    if u:
        spec["usage"] = None
        return _t("warning_deletion", "usage_warning", f"删除了食用方法/注意事项「{u}」")
    return None


FOOD_OPS = {
    "efficacy_exaggeration": op_efficacy, "allergen_deletion": op_allergen, "production_date_tamper": op_prod_date,
    "shelf_life_tamper": op_shelf, "ingredient_order_tamper": op_ing_order, "nutrition_value_tamper": op_nutrition,
    "claim_nutrition_conflict": op_claim_conflict, "quantity_tamper": op_quantity, "standard_number_tamper": op_standard,
    "batch_number_tamper": op_batch, "manufacturer_info_tamper": op_manufacturer, "storage_condition_tamper": op_storage,
    "product_attribute_tamper": op_attr, "target_population_tamper": op_population, "warning_deletion": op_warning,
}
