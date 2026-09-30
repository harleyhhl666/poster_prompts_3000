"""Scenes: 保健品说明 (supplement), 公益海报 (welfare), 活动宣传 (event)."""
import copy
import json
import re
import datetime as dt
from common import rng_for, fmt_date, shelf_str, money, md_cn, weekday_cn, add_days, add_months, expiry_of, build_nutrition, nutrition_rows, fmt_num
import brands as B
from visual import PALETTES, PHOTO_ARTIFACTS, REALISM, TEXT_RULE_BASE, TEXT_RULE_TABLE, TEXT_RULE_QUOTE, FONT_NOTE
from food import allergen_text, batch_code, recode_batch, ean13
from scenes_food import Q, QL, anomaly_note, text_rules

WARN = "保健食品不是药物，不能代替药物治疗疾病。"
ALW = {"麸质": ("麸质", "小麦"), "甲壳": ("甲壳", "虾"), "鱼": ("鱼", "鱼"), "蛋": ("蛋", "鸡蛋"), "花生": ("花生", "花生"),
       "大豆": ("大豆", "大豆"), "乳": ("乳", "乳"), "坚果": ("坚果", "坚果")}


def _t(type_, field, detail):
    return {"type": type_, "field": field, "detail": detail}


# ================================================================== supplements
GENERIC_NUT = {  # dataset-designed plausible bases for ordinary-food look-alikes (per 100 g / 100 mL)
    "固体饮料": ({"protein": 6.0, "fat": 1.2, "carb": 82.0, "sodium": 60}, "100g"),
    "压片糖果": ({"protein": 1.0, "fat": 1.5, "carb": 88.0, "sodium": 25}, "100g"),
    "凝胶糖果": ({"protein": 4.5, "fat": 0.2, "carb": 74.0, "sodium": 35}, "100g"),
    "饮品": ({"protein": 0.6, "fat": 0.0, "carb": 9.5, "sodium": 22}, "100mL"),
    "口服液": ({"protein": 0.8, "fat": 0.0, "carb": 10.5, "sodium": 18}, "100mL"),
}


def supp_nut_kind(s):
    if s["reg_type"] == "运动营养食品":
        return "运动营养食品"
    df = s["dosage_form"]
    for k in GENERIC_NUT:
        if k in df or k in "".join(s["names"]):
            return k
    return "固体饮料" if "粉" in df else ("饮品" if "液" in df or "饮" in df else "压片糖果")


def make_supp_spec(s, gid, brand, ref):
    rng = rng_for("supp", gid)
    sp = {"id": s["id"], "reg_type": s["reg_type"], "brand": brand}
    ni = rng.randrange(len(s["names"]))
    core = s["names"][ni]
    is_hf = s["reg_type"].startswith("保健食品")
    sp["name"] = f"{brand}牌{core}" if is_hf else f"{brand} {core}"
    sp["name_core"] = core
    sp["dosage_form"] = s["dosage_form"]
    specs = list(s["spec"])
    mb = re.search(r"营养成分表（每(?:袋|份|粒|片|瓶)([\d.]+)(g|mL)）", s["components"])
    if mb:
        m_ = [x for x in specs if x.startswith(f"{mb.group(1)}{mb.group(2)}/") or f"{mb.group(1)}{mb.group(2)}×" in x]
        specs = m_ or specs
    sp["spec"] = rng.choice(specs)
    sp["price"] = float(f"{int(rng.uniform(*s['price']))}.0")
    sp["raw"] = s["raw_materials"]
    sp["raw_tamper"] = s["hero_first_tamper"]
    sp["allergens"] = [ALW[a] for a in s["allergens"] if a in ALW]
    sp["allergen_statement"] = allergen_text(sp["allergens"], rng.randrange(3)) if sp["allergens"] else None
    sp["allergen_free_claim"] = None
    sp["components"] = s["components"].replace("×10^9", "×10⁹").replace("×10^10", "×10¹⁰").replace("×10^8", "×10⁸")
    sp["function"] = s["health_function"]
    sp["suitable"] = s["suitable"]
    sp["unsuitable"] = s["unsuitable"]
    sp["usage"] = s["usage"]
    sp["cautions"] = [c for c in s["cautions"] if s["reg_type"].startswith("保健食品") or "代替药物" not in c]
    sp["shelf"] = list(s["shelf"])
    sp["shelf_tamper"] = list(s["shelf_tamper"])
    sp["storage"] = s["storage"]
    from consistency import nutrient_mention_ok, kw_missing as _kwm
    raw_all = s["raw_materials"] + s["components"]
    nc = [x for x in s["normal_copy"] if nutrient_mention_ok(x, ["energy", "protein", "fat", "carb", "sodium", "calcium", "zinc", "vitd", "vitc", "iron", "fiber"])
          and not _kwm(x, [raw_all])]
    sp["normal_copy"] = nc or [f"规格{rng.choice(s['spec'])}", s["dosage_form"] + "，方便服用"]
    rng.shuffle(sp["normal_copy"])
    rng.shuffle(sp["cautions"])
    sp["exag_subtle"] = s["exag_subtle"]
    sp["exag_strong"] = s["exag_strong"]
    sp["pop_tamper"] = s["population_tamper"]
    sp["attr_tamper"] = s.get("attr_tamper")
    sp["attr_text"] = None
    sp["visual"] = s["visual"]
    sp["headline_extra"] = []
    sp["warning"] = WARN if is_hf else None
    sp["warning_weak"] = False
    back = rng.randint(20, 120)
    sp["prod_date"] = add_days(ref["start"], -back)
    sp["prod_true"] = sp["prod_date"]
    sp["expiry"] = expiry_of(sp["prod_date"], sp["shelf"][0], sp["shelf"][1])
    sp["expiry_true"] = sp["expiry"]
    abbr = rng.choice("ABDEFGHJKMNPRTWXYZ") + rng.choice("ABDEFGHJKMNPRTWXYZ")
    sp["abbr"] = abbr
    code, (lab,) = batch_code(rng, sp["prod_date"], rng.randrange(4), abbr)
    sp["batch"], sp["batch_label"], sp["batch_true"] = code, lab, code
    co = B.company(rng, "health")
    sp["mfr"] = co
    sp["mfr_addr2"] = None
    sp["phone"] = B.phone400(rng)
    sp["service_time"] = rng.choice(["周一至周五 9:00—17:30", "每日 8:30—20:00", "工作日 9:00—18:00"])
    prov = co["addr"]["prov"]
    pc = B.PROV_CODE.get(prov, "33")
    if s["reg_type"] == "保健食品-注册":
        sp["approval"] = f"国食健注G{rng.choice([2019, 2020, 2021, 2022, 2023, 2024])}{rng.randint(1, 999):04d}"
    elif s["reg_type"] == "保健食品-备案":
        sp["approval"] = f"食健备G{rng.choice([2021, 2022, 2023, 2024, 2025])}{pc}{rng.randint(1, 9999):06d}"
    else:
        sp["approval"] = None
    sp["approval2"] = None
    sp["standard"] = f"Q/{abbr}{rng.choice('SJKT')} {rng.randint(1, 80):04d}S-{rng.choice([2023, 2024, 2025])}"
    sp["standard2"] = None
    ptxt = s["dosage_form"] + "".join(s["names"])
    cat = 27 if s["reg_type"].startswith("保健食品") else (13 if "糖果" in ptxt else (6 if any(k in ptxt for k in ["饮料", "饮品", "口服液"]) else 31))
    sp["license"] = B.sc_license_city(rng, cat, co["addr"]["city"])
    sp["ean"] = ean13(rng)
    sp["tested_note"] = None
    parsed = parse_lib_nutrition(s["components"])
    sp["nut_from_lib"] = False
    if parsed:
        pre, basis, vals = parsed
        for k in ("energy", "protein", "fat", "carb", "sodium"):
            vals.setdefault(k, 0.0)
        sp["components"] = pre or None
        sp["nut"] = {k: (int(v) if k in ("energy", "sodium", "calcium") else v) for k, v in vals.items()}
        e = 17 * vals["protein"] + 37 * vals["fat"] + 17 * vals["carb"] + 8 * vals.get("fiber", 0)
        sp["nut"]["energy"] = int(round(e)) if e > 17 else 0  # keep energy consistent with the macros shown
        sp["nut_basis"] = "每" + basis.lstrip("每") if not basis.startswith("每") else basis
        sp["nut_from_lib"] = True
        sp["product_type"] = supp_nut_kind(s) if not is_hf else "保健食品"
    elif not is_hf:
        k = supp_nut_kind(s)
        base, basis = GENERIC_NUT.get(k, GENERIC_NUT["固体饮料"])
        sp["nut_basis"] = "每100mL" if basis == "100mL" else "每100g"
        keys = ["energy", "protein", "fat", "carb", "sodium"]
        sp["nut_keys"] = keys
        sp["nut"] = build_nutrition(base, keys, rng, jitter=0.1)
        sp["product_type"] = k
    else:
        sp["nut"] = None
        sp["product_type"] = "保健食品"
    return sp


NUTK = {"能量": "energy", "蛋白质": "protein", "脂肪": "fat", "碳水化合物": "carb", "钠": "sodium", "膳食纤维": "fiber",
        "维生素C": "vitc", "钙": "calcium", "锌": "zinc", "铁": "iron", "维生素D": "vitd"}


def parse_lib_nutrition(comp):
    """'…；营养成分表（每袋20g）：能量 320kJ、蛋白质 0g…' -> (prefix_text, basis_label, {key: value}) or None."""
    m = re.search(r"营养成分表（([^）]+)）[：:](.+)$", comp)
    if not m:
        return None
    basis = m.group(1)
    vals = {}
    for nm, v, u in re.findall(r"([\u4e00-\u9fa5A-Z]+)\s*([\d.]+)\s*(kJ|mg|μg|g)", m.group(2)):
        k = NUTK.get(nm)
        if k:
            vals[k] = float(v)
    pre = comp[:m.start()].rstrip("；;，, ")
    return pre, basis, vals


def supp_nut_lines(sp):
    if sp.get("nut_from_lib"):
        order = ["energy", "protein", "fat", "carb", "fiber", "sodium", "vitc", "calcium", "zinc", "iron", "vitd"]
        rows = nutrition_rows(sp["nut"], [k for k in order if k in sp["nut"]])
        return [f"{r['name']}｜{fmt_num(r['key'], r['value'])} {r['unit']}｜{r['nrv']}" for r in rows]
    rows = nutrition_rows(sp["nut"], sp["nut_keys"])
    return [f"{r['name']}｜{fmt_num(r['key'], r['value'])} {r['unit']}｜{r['nrv']}" for r in rows]


def supp_label_lines(sp):
    L = []
    L.append(f"产品名称：{sp['name']}")
    if sp["reg_type"].startswith("保健食品"):
        L.append(("原料：" if True else "") + sp["raw"])
        if sp["components"]:
            L.append(f"功效成分/标志性成分含量：{sp['components']}")
        if sp["function"]:
            L.append(f"保健功能：{sp['function']}")
    else:
        L.append(f"产品类型：{sp['product_type']}")
        L.append("配料：" + sp["raw"])
        if sp["components"]:
            L.append(sp["components"])
    if sp["allergen_statement"]:
        L.append(sp["allergen_statement"])
    L.append(f"适宜人群：{sp['suitable']}")
    if sp["unsuitable"]:
        L.append(f"不适宜人群：{sp['unsuitable']}")
    L.append(f"食用量及食用方法：{sp['usage']}")
    L.append(f"规格：{sp['spec']}")
    L.append(f"贮藏方法：{sp['storage']}")
    L.append(f"保质期：{shelf_str(*sp['shelf'])}")
    cs = [c.rstrip("。；; ") for c in sp["cautions"] if c.rstrip("。") != WARN.rstrip("。")]
    if not sp["reg_type"].startswith("保健食品"):
        cs = [c for c in cs if "代替药物" not in c]
    if cs:
        L.append("注意事项：" + "；".join(cs) + "。")
    L.append(f"生产日期：{fmt_date(sp['prod_date'], 'cn0')}")
    L.append(f"保质期至：{fmt_date(sp['expiry'], 'cn0')}")
    L.append(f"{sp['batch_label']}：{sp['batch']}")
    L.append(f"产品标准号：{sp['standard']}")
    if sp["standard2"]:
        L.append(f"执行标准：{sp['standard2']}")
    L.append(f"生产企业：{sp['mfr']['name']}")
    L.append(f"生产地址：{sp['mfr_addr2'] or sp['mfr']['addr']['text']}")
    L.append(f"食品生产许可证编号：{sp['license']}")
    L.append(f"投诉服务电话：{sp['phone']}（服务时段：{sp['service_time']}）")
    return L


def blue_hat(sp):
    if sp["approval"]:
        return f"天蓝色“小蓝帽”保健食品标志图形，标志下方两行小字：{Q('保健食品')}、{Q(sp['approval'])}"
    if sp.get("fake_hat"):
        return f"一个与保健食品标志相似的天蓝色帽形图案，下方小字：{Q(sp['fake_hat'])}"
    return None


def warning_zone(sp):
    if not sp["warning"]:
        return None
    if sp["warning_weak"]:
        return f"包装底部边缘一行极小的浅灰色字：{Q(sp['warning'])}"
    return f"主要展示面下部设置一个面积约占该面20%的警示用语区（白底黑框、黑体字，与背景有明显色差），内容：{Q(sp['warning'])}"


SUPP_SCENES = [
    ("box_pair", "保健食品包装正背面", ["16:9", "4:3"], "studio", "保健品外包装纸盒的正面与侧/背面并列展示（左正面、右背面），摄影棚柔光"),
    ("bottle", "保健食品瓶身标签", ["3:4", "4:5"], "studio", "保健品塑料瓶/玻璃瓶身标签特写，标签随瓶身弧面弯曲，中间信息区正对镜头"),
    ("leaflet", "产品说明书", ["3:4"], "studio", "一张平铺在浅色桌面上的保健食品说明书（折叠说明书展开后的正面），俯拍，纸张有轻微折痕"),
    ("ecom", "保健品电商详情页", ["9:16"], "flat", "一张保健品电商详情页长图（手机端竖版，多个模块自上而下）"),
    ("pharmacy_poster", "药店/专柜宣传海报", ["3:4", "4:5"], "scene", "连锁药店保健食品专柜旁立着的宣传海报实拍，背景为虚化的货架"),
    ("live_card", "直播间商品卡", ["9:16"], "flat", "直播带货画面风格的竖版商品信息卡（无真人，只有商品图与信息卡）"),
    ("sachet", "袋装/条装标签", ["1:1", "4:5"], "studio", "盒子与数条单独小袋并排平铺，重点展示盒子背面信息"),
]


def render_supp(sp, g, tampers):
    rng = rng_for("supprender", g["gid"])
    key, subc, _, realism, desc = g["scene"]
    pal = PALETTES[g["palette"]]
    rl = "" if "摄影棚" in desc else REALISM[realism] + "；"
    if key in ("leaflet",):
        look = f"说明书为白底印刷，页眉与小标题使用产品包装主色（产品包装外观：{sp['visual']}，本图只展示说明书，不出现包装实物）"
    elif key in ("ecom", "live_card", "pharmacy_poster"):
        look = f"页面/海报背景配色：{pal}；产品包装外观保持为：{sp['visual']}"
    else:
        look = f"包装外观：{sp['visual']}，标签与信息区沿用包装主色，信息区为白底深色文字"
    P = [f"生成一张{g['aspect']}比例的{desc}。{rl}{look}。",
         f"产品为虚构品牌{Q(sp['brand'])}的{Q(sp['name'])}（剂型：{sp['dosage_form']}，规格{sp['spec']}）。"]
    bh = blue_hat(sp)
    wz = warning_zone(sp)
    copy_lines = list(sp["normal_copy"][:2])
    if sp["headline_extra"]:
        copy_lines = sp["headline_extra"] + copy_lines[:1]
    if sp.get("attr_text"):
        copy_lines.append(sp["attr_text"])
    if sp.get("allergen_free_claim"):
        copy_lines.append(sp["allergen_free_claim"])
    if sp.get("tested_note"):
        copy_lines.append(sp["tested_note"])
    copy_lines = list(dict.fromkeys(copy_lines))
    lab = supp_label_lines(sp)
    raw_line_key = "原料：" if sp["reg_type"].startswith("保健食品") else "配料："
    if key in ("box_pair", "sachet"):
        front = []
        if bh:
            front.append("正面左上角为" + bh)
        front.append(f"正面中部大字品名{Q(sp['name'])}")
        if sp["function"]:
            front.append(f"品名下方的色带写{Q('保健功能：' + sp['function'])}")
        front.append("产品图下方宣传短句：" + QL(copy_lines, "、"))
        front.append(f"右下角{Q(sp['spec'])}")
        if wz:
            front.append(wz)
        P.append("【包装正面】" + "；".join(front) + "。")
        P.append("【包装背面/侧面】白底信息区，按以下顺序分行排版（左侧为文字说明，右侧留出条形码与二维码）：" + "；".join(Q(x) for x in lab) +
                 f"；右下角条形码数字{Q(sp['ean'])}。")
        if sp.get("nut"):
            P.append(f"背面右侧营养成分表（表头{Q('项目')}｜{Q(sp['nut_basis'])}｜{Q('营养素参考值%')}）逐行：" + "；".join(Q(x) for x in supp_nut_lines(sp)) + "。")
    elif key == "bottle":
        P.append("【瓶身标签左侧三分之一】" + ("顶部为" + bh + "；" if bh else "") + f"品名{Q(sp['name'])}；" + QL(copy_lines, "、") + "。")
        P.append("【瓶身标签中部】" + "；".join(Q(x) for x in lab[:10]) + "。")
        P.append("【瓶身标签右侧】" + "；".join(Q(x) for x in lab[10:]) + f"；竖排条形码{Q(sp['ean'])}。")
        if wz:
            P.append(wz.replace("主要展示面下部", "瓶身标签正面下部") + "。")
        if sp.get("nut"):
            P.append(f"中部信息下方的营养成分表（表头三列：{Q('项目')}｜{Q(sp['nut_basis'])}｜{Q('营养素参考值%')}）逐行：" + "；".join(Q(x) for x in supp_nut_lines(sp)) + "。")
    elif key == "leaflet":
        P.append("【说明书顶部】" + ("左上角为" + bh + "；" if bh else "") + f"居中标题{Q(sp['name'] + ' 说明书')}" + (f"；标题下方{Q('【保健功能】' + sp['function'])}" if sp["function"] else "") + "。")
        P.append("【正文】以“【字段名】内容”的格式逐条排版，两栏，字段名加粗：" + "；".join(Q("【" + x.split("：", 1)[0] + "】" + x.split("：", 1)[1]) if "：" in x else Q(x) for x in lab) + "。")
        if wz:
            P.append("说明书首段上方的黑框内写" + Q(sp["warning"]) + ("（字号很小、颜色很浅）" if sp["warning_weak"] else "（黑体加粗）") + "。")
        if sp.get("nut"):
            P.append(f"说明书右下角营养成分表（表头三列：{Q('项目')}｜{Q(sp['nut_basis'])}｜{Q('营养素参考值%')}）逐行：" + "；".join(Q(x) for x in supp_nut_lines(sp)) + "。")
        if copy_lines:
            P.append("说明书页脚一行宣传语：" + QL(copy_lines, "、") + "。")
    elif key in ("ecom", "live_card"):
        P.append("【头图】产品主图，右上角为" + (bh if bh else f"品牌标志{Q(sp['brand'])}") + f"；主标题{Q(sp['name'])}；卖点大字" + QL(copy_lines, "、") +
                 f"；价格条{Q('到手价 ¥' + money(sp['price']))}。")
        if sp["function"]:
            P.append(f"【保健功能卡片】{Q('保健功能：' + sp['function'])}" + (f"；{Q('功效成分：' + sp['components'])}" if sp["components"] else "") + "。")
        elif sp["components"]:
            P.append(f"【成分卡片】{Q(sp['components'])}。")
        P.append("【产品信息表（两列表格）】逐行：" + "；".join(Q(x) for x in lab) + "。")
        if sp.get("nut"):
            P.append(f"【营养成分表】（表头三列：{Q('项目')}｜{Q(sp['nut_basis'])}｜{Q('营养素参考值%')}）逐行：" + "；".join(Q(x) for x in supp_nut_lines(sp)) + "。")
        if wz:
            P.append("【页面底部】" + wz.replace("主要展示面下部设置一个面积约占该面20%的", "设置一个醒目的") + "。")
    else:  # pharmacy poster
        P.append("【海报上部】" + ("左上角为" + bh + "；" if bh else "") + f"大字品名{Q(sp['name'])}；宣传标语" + QL(copy_lines, "、") + "。")
        P.append(f"【海报中部】产品瓶/盒摄影；右侧价格标签{Q('专柜价 ¥' + money(sp['price']))}{Q('会员价 ¥' + money(round(sp['price']*0.88,0)-0.1))}。")
        P.append("【海报下部信息栏（白底小字，两栏）】" + "；".join(Q(x) for x in lab) + "。")
        if wz:
            P.append(wz.replace("主要展示面下部", "海报下部信息栏上方") + "。")
        if sp.get("nut"):
            P.append(f"【海报右下角营养成分表】（表头三列：{Q('项目')}｜{Q(sp['nut_basis'])}｜{Q('营养素参考值%')}）逐行：" + "；".join(Q(x) for x in supp_nut_lines(sp)) + "。")
    if sp.get("expiry_ink"):
        P.append(f"包装底部边缘有一行黑色点阵喷码（清晰可读）：{Q(sp['batch_true'] + ' 保质期至' + sp['expiry_ink'].strftime('%Y/%m/%d'))}。")
    if sp.get("approval2"):
        where = "背面条形码上方" if any(k in P[0] for k in ("包装", "瓶", "盒", "罐", "袋")) and "海报" not in P[0] else "画面最底部页脚小字行"
        P.append(f"另在{where}小字重复标示批准文号{Q(sp['approval2'])}。")
    if g["artifacts"]:
        P.append("真实感细节：" + "；".join(PHOTO_ARTIFACTS[a] for a in g["artifacts"]) + "。所有文字区域依然必须清晰锐利、可逐字辨认。")
    P.append(anomaly_note(tampers, "保健食品包装/宣传设计"))
    P.append(text_rules(bool(sp.get("nut"))))
    return "\n".join(P)


# ---- supplement tamper ops
def s_efficacy(sp, level, rng, ctx):
    if level == "subtle":
        line = rng.choice(sp["exag_subtle"])
        old = sp["normal_copy"][0]
        sp["normal_copy"][0] = line
        return _t("efficacy_exaggeration", "promo_copy", f"宣传短句「{old}」被替换为轻度夸大的「{line}」")
    lines = rng.sample(sp["exag_strong"], min(2, len(sp["exag_strong"])))
    sp["headline_extra"] = lines
    return _t("efficacy_exaggeration", "headline_claim", "加入疾病治疗/绝对化功效宣称：" + "；".join("「" + x + "」" for x in lines))


def s_function_upgrade(sp, level, rng, ctx):
    f = sp["function"]
    if not f or not f.startswith("有助于"):
        return None
    nf = f.replace("有助于", "有效" if level == "subtle" else "快速", 1)
    sp["function"] = nf
    return _t("efficacy_exaggeration", "health_function", f"保健功能用语由规范的「{f}」改为「{nf}」")


def s_allergen(sp, level, rng, ctx):
    if not sp["allergens"]:
        return None
    if level == "subtle" and len(sp["allergens"]) >= 2:
        rem = sp["allergens"].pop(rng.randrange(len(sp["allergens"])))
        sp["allergen_statement"] = allergen_text(sp["allergens"], 0)
        sp["cautions"] = [c for c in sp["cautions"] if rem[1] not in c]
        return _t("allergen_deletion", "allergen_statement", f"过敏原提示删除了「{rem[1]}」，原料中仍含对应成分")
    w = sp["allergens"][0][1]
    sp["allergen_statement"] = None
    sp["cautions"] = [c for c in sp["cautions"] if "过敏" not in c and "禁食" not in c]
    if level == "strong":
        sp["allergen_free_claim"] = "0致敏原 · 过敏体质可放心食用"
        return _t("allergen_deletion", "allergen_statement+front_claim", f"删除过敏原提示（原含{w}），并在正面宣称「0致敏原 · 过敏体质可放心食用」")
    return _t("allergen_deletion", "allergen_statement", f"删除了唯一的过敏原提示（{w}）")


def s_order(sp, level, rng, ctx):
    old = sp["raw"]
    if level == "subtle":
        items = [x.strip() for x in re.split("[、，]", old)]
        if len(items) < 3:
            return None
        i = rng.randrange(1, min(4, len(items)))
        items[i - 1], items[i] = items[i], items[i - 1]
        sp["raw"] = "、".join(items)
        return _t("ingredient_order_tamper", "raw_materials", f"原料表中「{items[i]}」与「{items[i-1]}」的先后顺序被调换")
    sp["raw"] = sp["raw_tamper"]
    return _t("ingredient_order_tamper", "raw_materials", f"原料表被整体重排，天然/功效感原料被前置：原「{old}」→「{sp['raw_tamper']}」")


def s_shelf(sp, level, rng, ctx):
    sv, su = sp["shelf"]
    tv, tu = sp["shelf_tamper"]
    if level == "subtle" or ctx.get("scene") == "leaflet":
        sp["shelf"] = [tv, tu]
        return _t("shelf_life_tamper", "shelf_life", f"保质期由{shelf_str(sv,su)}改为{shelf_str(tv,tu)}，「保质期至」仍按原保质期推算")
    sp["shelf"] = [tv, tu]
    sp["expiry_ink"] = sp["expiry"]
    sp["expiry"] = expiry_of(sp["prod_date"], tv, tu)
    return _t("shelf_life_tamper", "shelf_life+expiry",
              f"保质期由{shelf_str(sv,su)}延长为{shelf_str(tv,tu)}，印刷保质期至改为{fmt_date(sp['expiry'],'iso')}，但底部喷码仍为原保质期至{fmt_date(sp['expiry_ink'],'iso')}")


def s_prod(sp, level, rng, ctx):
    old = sp["prod_date"]
    if level == "subtle":
        new = add_days(old, rng.choice([-5, -3, 4, 6]))
        sp["prod_date"] = new
        sp["expiry"] = expiry_of(new, *sp["shelf"])
        return _t("production_date_tamper", "production_date", f"生产日期由{fmt_date(old,'iso')}改为{fmt_date(new,'iso')}，批号「{sp['batch']}」仍对应原日期")
    new = add_days(old, rng.randint(200, 320))
    sp["prod_date"] = new
    return _t("production_date_tamper", "production_date", f"生产日期被改晚为{fmt_date(new,'iso')}，但「保质期至」{fmt_date(sp['expiry'],'iso')}未变，与保质期{shelf_str(*sp['shelf'])}矛盾，批号亦不符")


def s_warning(sp, level, rng, ctx):
    if level == "subtle":
        c = [x for x in sp["cautions"] if ("代替药物" in x or "咨询" in x or "医生" in x or "推荐量" in x) and x.rstrip("。") != WARN.rstrip("。")]
        if c:
            sp["cautions"].remove(c[0])
            core = re.sub(r"[，。、；\s]", "", c[0])
            sp["cautions"] = [x for x in sp["cautions"] if core[:6] not in x]
            return _t("warning_deletion", "cautions", f"注意事项中删除了「{c[0]}」")
        if sp["warning"]:
            sp["warning_weak"] = True
            return _t("warning_deletion", "warning_zone", "警示用语被弱化为底部极小浅色字，不再是醒目的警示用语区")
        return None
    removed = []
    if sp["warning"]:
        sp["warning"] = None
        removed.append("警示用语区「保健食品不是药物，不能代替药物治疗疾病」")
    c = [x for x in sp["cautions"] if "代替药物" in x]
    for x in c:
        sp["cautions"].remove(x)
        removed.append(f"注意事项「{x}」")
    if not removed:
        return None
    return _t("warning_deletion", "warning_zone+cautions", "删除了" + "、".join(removed))


def s_pop(sp, level, rng, ctx):
    if level == "subtle" and sp["unsuitable"]:
        old = sp["unsuitable"]
        sp["unsuitable"] = None
        return _t("target_population_tamper", "unsuitable_population", f"删除了不适宜人群「{old}」")
    old = sp["suitable"]
    sp["suitable"] = sp["pop_tamper"]
    if sp["unsuitable"]:
        sp["unsuitable"] = None
    return _t("target_population_tamper", "suitable_population", f"适宜人群由「{old}」扩大为「{sp['pop_tamper']}」，并删除不适宜人群")


def s_approval(sp, level, rng, ctx):
    a = sp["approval"]
    if not a:
        if level == "strong":
            sp["fake_hat"] = f"国食健注G{rng.choice([2020, 2022, 2023])}{rng.randint(1, 999):04d}"
            sp["function"] = ctx["fake_function"]
            return _t("approval_number_tamper", "approval_number",
                      f"普通食品({sp['product_type']})印上仿冒的蓝帽图案与编号「{sp['fake_hat']}」，并标注保健功能「{ctx['fake_function']}」")
        return None
    if level == "subtle":
        digs = [i for i, ch in enumerate(a) if ch.isdigit()]
        i = digs[-2]
        na = a[:i] + str((int(a[i]) + 1) % 10) + a[i + 1:]
        sp["approval2"] = na
        return _t("approval_number_tamper", "approval_number", f"同一包装两处批准文号不一致：「{a}」与「{na}」")
    if a.startswith("食健备"):
        na = "国食健注G" + a[4:8] + a[-4:]   # 食健备G + YYYY + PP + NNNNNN -> 国食健注G + YYYY + NNNN
        sp["approval"] = na
        sp["function"] = ctx["fake_function"]
        return _t("approval_number_tamper", "approval_number+function",
                  f"营养素补充剂备案产品被改标为注册号格式「{na}」，并冒称注册类保健功能「{ctx['fake_function']}」")
    na = "国药准字" + rng.choice("HZ") + a[-8:]
    sp["approval"] = na
    return _t("approval_number_tamper", "approval_number", f"保健食品批准文号被改写为药品批准文号样式「{na}」（冒充药品）")


def s_attr(sp, level, rng, ctx):
    if sp["attr_tamper"]:
        sp["attr_text"] = sp["attr_tamper"]
        return _t("product_attribute_tamper", "product_attribute", f"加入不实属性宣称「{sp['attr_tamper']}」")
    if level == "strong":
        sp["attr_text"] = rng.choice(["医院专供 · 药准品质", "三甲医院营养科推荐", "临床验证有效率98.6%"])
        return _t("product_attribute_tamper", "product_attribute", f"加入冒充医疗背书的宣称「{sp['attr_text']}」")
    return None


def s_tested(sp, level, rng, ctx):
    sp["tested_note"] = rng.choice(["经权威机构检测 有效率96%", "10万人亲测有效"])
    return _t("unsubstantiated_claim", "evidence_claim", f"加入无依据的检测/效果数据「{sp['tested_note']}」")


def s_standard(sp, level, rng, ctx):
    s = sp["standard"]
    if level == "subtle":
        m = re.search(r"(\d{4}) ?S", s)
        d = m.group(1)
        nd = d[:-1] + str((int(d[-1]) + 2) % 10)
        sp["standard2"] = s.replace(d, nd, 1)
        return _t("standard_number_tamper", "standard_number", f"两处标准号不一致：{s} 与 {sp['standard2']}")
    beverage = any(k in sp["dosage_form"] + sp["name"] for k in ["饮料", "饮品", "口服液", "泡腾"])
    wrong, desc = (("GB 7100-2015", "饼干") if beverage else ("GB 7101-2022", "饮料"))
    sp["standard"] = wrong
    return _t("standard_number_tamper", "standard_number", f"标准号被替换为{desc}类食品安全国家标准{wrong}，与{sp['dosage_form']}产品类别不符")


def s_mfr(sp, level, rng, ctx):
    a = sp["mfr"]["addr"]
    if level == "strong":
        alt = next(c for c in B.CITIES if c[0] != a["prov"])
        alt = B.address_in(rng, rng.choice([c for c in B.CITIES if c[0] != a["prov"]])[1])
        sp["mfr_addr2"] = alt["text"]
        return _t("manufacturer_info_tamper", "manufacturer_address",
                  f"生产地址被改为外省地址「{alt['text']}」，与生产企业名称所在城市「{a['city']}」及许可证省份代码不符")
    oc = rng.choice([c for c in B.CITIES if c[1] != a["city"]])[1]
    sp["mfr_addr2"] = a["text"].replace(a["city"], oc, 1)
    return _t("manufacturer_info_tamper", "manufacturer_address", f"生产地址城市被改为「{oc}」，与企业名称所在城市「{a['city']}」不符")


SUPP_OPS = {"efficacy_exaggeration": s_efficacy, "function_upgrade": s_function_upgrade, "allergen_deletion": s_allergen,
            "ingredient_order_tamper": s_order, "shelf_life_tamper": s_shelf, "production_date_tamper": s_prod,
            "warning_deletion": s_warning, "target_population_tamper": s_pop, "approval_number_tamper": s_approval,
            "product_attribute_tamper": s_attr, "unsubstantiated_claim": s_tested, "standard_number_tamper": s_standard,
            "manufacturer_info_tamper": s_mfr}


# ================================================================== welfare posters
ORG_KIND_SUFFIX = {"社区卫生服务中心": "社区卫生服务中心", "街道办事处": "街道办事处", "疾病预防控制中心": "疾病预防控制中心",
                   "市场监督管理局": "市场监督管理所", "市场监管": "市场监督管理所", "学校": "", "消费者协会": "消费者权益保护协会",
                   "营养学会": "营养健康促进会", "志愿者协会": "青年志愿者协会", "卫生健康": "卫生健康服务中心", "医院": "人民医院"}


def org_name(rng, kind, place=None):
    """place: dict from brands.fict_place (city real prefecture, district/street fictional) -> all names share one locality."""
    pl = place or B.fict_place(rng)
    city, dist, street = pl["city"], pl["district"], pl["street"]
    if "学校" in kind:
        return f"{city}{dist}{rng.choice(B.SCHOOLS)}"
    if "街道" in kind:
        return f"{city}{dist}{street}办事处"
    if "社区卫生" in kind:
        return f"{city}{dist}{street}社区卫生服务中心"
    if "疾病预防" in kind:
        return f"{city}{dist}疾病预防控制中心"
    if "市场监" in kind:
        return f"{city}{dist}市场监督管理局"
    if "消费者" in kind:
        return f"{city}{dist}消费者权益保护委员会"
    if "营养" in kind:
        return f"{city}营养健康促进会"
    if "志愿" in kind:
        return f"{city}{dist}青年志愿者协会"
    if "医院" in kind:
        return f"{city}{dist}人民医院"
    if "妇幼" in kind:
        return f"{city}{dist}妇幼保健院"
    if "派出所" in kind or "公安" in kind:
        return f"{city}{dist}公安分局{street.replace('街道', '')}派出所"
    if "老年" in kind:
        return f"{city}{dist}老年协会"
    if "食堂" in kind:
        return f"{city}{dist}机关事务服务中心"
    if "卫生健康" in kind:
        return f"{city}{dist}卫生健康局"
    if "妇联" in kind or "妇女" in kind:
        return f"{city}{dist}妇女联合会"
    if "教育" in kind:
        return f"{city}{dist}教育局"
    if "红十字" in kind:
        return f"{city}{dist}红十字会"
    if "居委" in kind or "社区" in kind:
        return f"{city}{dist}{street}{rng.choice(['幸福里', '和平里', '锦绣', '翠苑'])}社区居民委员会"
    return f"{city}{dist}{kind}"


def local_venue(rng, pl):
    return f"{pl['city']}{pl['district']}{pl['street']}{rng.choice(['社区文化活动中心一楼多功能厅', '邻里中心广场', '社区卫生服务中心三楼健康教育室', '党群服务中心二楼会议室', '文化广场'])}"


WELF_SCENES = [
    ("board", "政务/社区宣传栏", ["4:3", "16:9"], "scene", "社区宣传栏玻璃框内张贴的公益宣传海报实拍照"),
    ("hospital", "医疗科普海报", ["3:4"], "scene", "社区卫生服务中心候诊区墙面上的科普海报实拍照"),
    ("school", "校园展板", ["16:9", "4:3"], "scene", "学校走廊/食堂门口的易拉宝或KT板展板实拍照"),
    ("flat", "公益宣传海报", ["3:4", "4:5"], "flat", "一张公益宣传海报平面设计稿"),
    ("wechat", "公众号科普长图", ["9:16"], "flat", "一张手机公众号推文风格的科普长图（竖版，分模块）"),
    ("folding", "宣传折页", ["16:9"], "flat", "一张三折页宣传单展开后的内页（横版，三栏）"),
    ("metro", "灯箱广告", ["16:9"], "scene", "地铁站通道内公益灯箱海报实拍，灯箱发光均匀"),
    ("elevator", "电梯框架海报", ["3:4"], "phone", "居民楼电梯内框架广告位中的公益海报，被人用手机正面拍下"),
]
WELF_STYLE = {"社区公益风": "温暖亲和的社区公益风，扁平插画人物与图标", "医疗科普风": "专业清爽的医疗科普风，蓝绿配色、图标化要点",
              "政务宣传栏风": "规整庄重的政务宣传栏风，红色标题条、分栏排版", "亲子卡通风": "明快的亲子卡通风，圆润插画",
              "校园风": "活泼的校园风，手绘黑板与便签元素", "极简信息图风": "极简信息图风，大号数字与图标"}


METRO_CITIES = ["上海市", "天津市", "重庆市", "长沙市", "沈阳市", "长春市", "南宁市", "佛山市", "石家庄市", "南通市", "呼和浩特市", "嘉兴市"]


def make_welfare_spec(w, gid, ref, scene_key=None):
    rng = rng_for("welf", gid)
    titles = [t for t in w["titles"] if ref["season_fn"](rng, t) is not None] or w["titles"]
    sp = {"id": w["id"], "title": rng.choice(titles), "subtitle": rng.choice(w["subtitles"]) if w["subtitles"] else None}
    d0 = ref["season_fn"](rng, sp["title"] + " " + w["sub_category"])
    if d0 is not None:
        ref = dict(ref, start=d0)
    sp["seasonal_ok"] = ref["season_fn"](rng, sp["title"]) is not None
    secs = copy.deepcopy(w["sections"])
    keytexts = [n["text"] for n in w["numbers"]] + [w["key_warning"] or ""]
    first, rest = secs[0], secs[1:]
    rng.shuffle(rest)
    secs = [first] + rest
    for s in secs:
        items = s["items"]
        if not any(w in s["heading"] for w in ["八类", "八大", "步"]):
            rng.shuffle(items)
        droppable = [x for x in items if not any(k and k in x for k in keytexts)]
        complete_list = any(w in s["heading"] for w in ["八类", "八大", "24项", "五步", "四步", "三步"])
        if len(items) >= 4 and droppable and rng.random() < 0.6 and not complete_list:
            items.remove(rng.choice(droppable))
    if sp.get("subtitle"):
        for s_ in secs:
            s_["items"] = [x for x in s_["items"] if x != sp["subtitle"]] or s_["items"]
    sp["sections"] = secs
    kinds = w["organizer_types"]
    pl = B.fict_place(rng)
    if scene_key == "metro" and pl["city"] not in METRO_CITIES:
        pl["city"] = rng.choice(METRO_CITIES)
    sp["place"] = pl
    k1 = rng.choice(kinds)
    sp["organizer"] = org_name(rng, k1, pl)
    k2 = rng.choice([k for k in kinds if k != k1] or kinds)
    sp["co_organizer"] = org_name(rng, k2, pl) if rng.random() < 0.6 else None
    if sp["co_organizer"] == sp["organizer"]:
        sp["co_organizer"] = None
    sp["numbers"] = copy.deepcopy(w["numbers"])
    sp["key_warning"] = w["key_warning"]
    sp["misinfo_subtle"], sp["misinfo_strong"] = w["misinfo_subtle"], w["misinfo_strong"]
    sp["cta"] = w["cta"]
    complaint = any(x in w["sub_category"] + w["id"] for x in ["保健品", "虚假", "防骗", "标签", "临期", "网购", "直播", "农贸", "外卖", "fraud", "label"])
    sp["hotline_label"] = "投诉举报电话" if complaint else "咨询电话"
    sp["hotline"] = "12315" if (complaint and rng.random() < 0.6) else B.city_phone(rng, pl["city"])
    sp["hotline2"] = None
    sp["hotline_dup"] = None
    sp["source_note"] = next((n.get("source") for n in w["numbers"] if n.get("source")), None)
    sp["style"] = rng.choice(w["visual_styles"])
    sp["motif"] = w["visual_motif"]
    sp["event"] = None
    if w["has_event"]:
        kind = rng.choice(w.get("event_kinds") or ["主题宣传活动"])
        day = ref["start"]
        venue = local_venue(rng, pl)
        t = rng.choice(["9:00—11:30", "14:30—16:30", "9:30—11:30", "15:00—17:00"])
        sp["event"] = {"kind": kind, "date": day, "time": t, "venue": venue, "venue2": None, "date2": None, "weekday": None,
                       "quota": rng.choice([30, 40, 50, 60, 80]), "quota2": None,
                       "reg": f"报名电话：{sp['hotline'] if sp['hotline'] != '12315' else B.city_phone(rng, pl['city'])}"}
    sp["poster_code"] = f"宣传资料编号：{rng.choice(['JK', 'SA', 'YY', 'KP'])}-{ref['start'].year}-{rng.randint(1, 99):03d}"
    sp["inserted"] = []
    sp["warning_on"] = True
    return sp


def render_welfare(sp, g, tampers):
    key, subc, _, realism, desc = g["scene"]
    pal = PALETTES[g["palette"]]
    st = WELF_STYLE.get(sp["style"], sp["style"])
    colour_in_style = any(c in st for c in ["色", "配色", "红", "蓝", "绿", "黄", "金", "牛皮纸", "复古", "烫金", "水墨"])
    pal_txt = "" if colour_in_style else f"；配色：{pal}"
    P = [f"生成一张{g['aspect']}比例的{desc}。{REALISM[realism]}。视觉风格：{st}{pal_txt}；插画/图形元素：{sp['motif']}。",
         "这是一张非商业公益宣传海报，不出现任何商品品牌或价格。"]
    top = [f"顶部主办单位标识行{Q('主办：' + sp['organizer'])}" + (f"、{Q('协办：' + sp['co_organizer'])}" if sp["co_organizer"] else "")]
    top.append(f"大标题{Q(sp['title'])}")
    if sp["subtitle"]:
        top.append(f"副标题{Q(sp['subtitle'])}")
    P.append("【标题区】" + "；".join(top) + "。")
    secs = sp["sections"]
    if key == "folding":
        cols = ["左栏", "中栏", "右栏"]
        for i, s in enumerate(secs):
            col = cols[min(i, 2)]
            P.append(f"【{col}·小标题{Q(s['heading'])}】要点逐条（带圆点）：" + "；".join(Q(x) for x in s["items"]) + "。")
    else:
        pos = ["左上", "右上", "左下", "右下", "中部通栏"] if key in ("board", "school", "metro") else ["第1块", "第2块", "第3块", "第4块", "第5块"]
        for i, s in enumerate(secs):
            P.append(f"【内容{pos[i % len(pos)]}·小标题{Q(s['heading'])}】要点逐条（配小图标）：" + "；".join(Q(x) for x in s["items"]) + "。")
    if sp["warning_on"] and sp["key_warning"]:
        P.append(f"【重点提示条（醒目色块）】{Q(sp['key_warning'])}。")
    ev = sp["event"]
    if ev:
        d = ev["date"]
        wd = ev["weekday"] or weekday_cn(d)
        head = f"{d.year}年{md_cn(d)}（{wd}）{ev['time']}"
        lines = [f"活动名称：{ev['kind']}", f"活动时间：{head}", f"活动地点：{ev['venue']}", f"名额：限{ev['quota']}人，免费参加", ev["reg"]]
        P.append("【活动信息框（海报下部）】" + "；".join(Q(x) for x in lines) + "。")
        foot = []
        if ev["date2"] or ev["venue2"] or ev["quota2"]:
            d2 = ev["date2"] or d
            foot.append(f"{d2.year}年{md_cn(d2)} {ev['time']}")
            foot.append(ev["venue2"] or ev["venue"])
            if ev["quota2"]:
                foot.append(f"限{ev['quota2']}人")
            P.append("【底部报名二维码旁小字】" + Q(f"{ev['kind']}：" + "，".join(foot)) + "。")
    bottom = [sp["cta"], f"{sp['hotline_label']}：{sp['hotline']}"]
    if sp["hotline2"]:
        bottom.append(f"联系人电话：{sp['hotline2']}")
    if sp.get("hotline_dup") and not sp.get("event"):
        bottom.append(f"扫码或致电{sp['hotline_dup']}了解更多")
    if sp["source_note"]:
        bottom.append(f"资料来源：{sp['source_note']}")
    bottom.append(sp["poster_code"])
    P.append("【页脚】二维码图形；" + "；".join(Q(x) for x in bottom) + "。")
    if g["artifacts"]:
        P.append("真实感细节：" + "；".join(PHOTO_ARTIFACTS[a] for a in g["artifacts"]) + "。所有文字依然必须清晰可读。")
    P.append(anomaly_note(tampers, "公益宣传海报"))
    P.append(text_rules(False))
    return "\n".join(P)


def _replace_text(sp, old, new):
    if sp["subtitle"] and old in sp["subtitle"]:
        sp["subtitle"] = sp["subtitle"].replace(old, new)
        return True
    for s in sp["sections"]:
        for i, x in enumerate(s["items"]):
            if old in x:
                s["items"][i] = x.replace(old, new)
                return True
    return False


def w_fact(sp, level, rng, ctx):
    for n in sp["numbers"]:
        if _replace_text(sp, n["text"], n["tampered"]):
            return _t("health_fact_tamper", "key_fact", f"关键知识点「{n['text']}」被改为错误的「{n['tampered']}」")
    return None


def w_misinfo(sp, level, rng, ctx):
    line = sp["misinfo_subtle"] if level == "subtle" else sp["misinfo_strong"]
    cands = [x for x in sp["sections"] if not any(w in x["heading"] for w in ["八类", "八大", "步"])] or sp["sections"]
    s = cands[rng.randrange(len(cands))]
    s["items"].insert(rng.randrange(1, len(s["items"]) + 1), line)
    return _t("misinformation_insertion", "section_item", f"在「{s['heading']}」板块中自然插入错误说法「{line}」")


def w_warning(sp, level, rng, ctx):
    if not sp["key_warning"]:
        return None
    sp["warning_on"] = False
    core = re.sub(r"[，。、；！\s请]", "", sp["key_warning"])
    grams = {core[i:i + 4] for i in range(max(1, len(core) - 3))}
    for s_ in sp["sections"]:
        s_["items"] = [x for x in s_["items"] if not any(g in re.sub(r"[，。、；！\s请]", "", x) for g in grams)] or s_["items"][:1]
    return _t("warning_deletion", "key_warning", f"删除了重点提示「{sp['key_warning']}」及正文中与之相同的提示语")


def w_event(sp, level, rng, ctx):
    ev = sp["event"]
    if not ev:
        return None
    r = rng.random()
    if level == "subtle":
        if r < 0.5:
            ev["weekday"] = weekday_cn(add_days(ev["date"], 1))
            return _t("event_date_tamper", "event_weekday", f"活动日期{md_cn(ev['date'])}实际为{weekday_cn(ev['date'])}，画面标注为（{ev['weekday']}）")
        ev["date2"] = add_days(ev["date"], rng.choice([1, 7, -1]))
        return _t("event_date_tamper", "event_date", f"活动信息框日期{md_cn(ev['date'])}，底部报名处写{md_cn(ev['date2'])}，两处不一致")
    ev["venue2"] = f"{rng.choice(B.ORG_PLACE)}社区文化活动中心二楼"
    ev["date2"] = add_days(ev["date"], 7)
    return _t("event_date_tamper", "event_date+venue", f"底部报名信息的日期（{md_cn(ev['date2'])}）与地点（{ev['venue2']}）均与活动信息框不一致")


def w_contact(sp, level, rng, ctx):
    if sp["hotline"] == "12315" and level == "subtle":
        sp["hotline"] = "12351"
        return _t("contact_info_tamper", "hotline", "投诉举报电话12315被写成「12351」")
    if level == "strong":
        sp["hotline2"] = f"{B.city_phone(rng, sp['place']['city'])}（{rng.choice(['王老师', '李经理'])}，可上门讲解、代购产品）"
        return _t("contact_info_tamper", "hotline", f"页脚加入私人联系电话「{sp['hotline2']}」替代官方渠道（正确投诉渠道为12315）")
    h = sp["hotline"]
    nh = h[:-1] + str((int(h[-1]) + 3) % 10)
    sp["hotline_dup"] = nh
    if sp.get("event"):
        sp["event"]["reg"] = f"报名电话：{nh}"
        where = "活动信息框报名电话"
    else:
        where = "二维码旁重复的电话"
    return _t("contact_info_tamper", "hotline", f"页脚{sp['hotline_label']}「{h}」与{where}「{nh}」末位不一致")


def w_quota(sp, level, rng, ctx):
    ev = sp["event"]
    if not ev:
        return None
    ev["quota2"] = ev["quota"] + (20 if level == "subtle" else 150)
    return _t("quota_contradiction", "quota", f"活动名额前后矛盾：信息框限{ev['quota']}人，底部写限{ev['quota2']}人")


def w_source(sp, level, rng, ctx):
    if not sp["source_note"]:
        return None
    old = sp["source_note"]
    sp["source_note"] = old.replace("2022", "2016") if "2022" in old else "网络资料整理"
    return _t("source_attribution_tamper", "source_note", f"资料来源由「{old}」改为「{sp['source_note']}」")


WELF_OPS = {"health_fact_tamper": w_fact, "misinformation_insertion": w_misinfo, "warning_deletion": w_warning,
            "event_date_tamper": w_event, "contact_info_tamper": w_contact, "quota_contradiction": w_quota,
            "source_attribution_tamper": w_source}


# ================================================================== event posters
EVENT_SCENES = [
    ("flat", "活动海报", ["3:4", "4:5"], "flat", "一张活动宣传海报平面设计稿"),
    ("standee", "活动展架", ["9:16"], "scene", "活动现场入口处易拉宝展架的实拍照，背景为虚化的场地"),
    ("wechat", "活动推文长图", ["9:16"], "flat", "一张手机端活动推文/报名页长图"),
    ("mall_screen", "商场LED/灯箱", ["16:9"], "scene", "商场中庭灯箱/大屏上显示的活动海报，被正面拍摄"),
    ("flyer", "活动宣传单", ["3:4"], "phone", "一张被手拿着的A4活动宣传单页，手机实拍"),
    ("board", "社区公告栏", ["4:3"], "scene", "社区公告栏上张贴的活动通知海报实拍"),
    ("banner", "横版活动主视觉", ["16:9"], "flat", "一张横版活动主视觉KV（适合网页banner或大屏）"),
]
EVENT_STYLE = {"商场促销风": "热闹的商场促销风，大号标题与彩带元素", "年轻潮流风": "年轻潮流风，撞色几何与贴纸元素",
               "社区公益风": "亲和的社区公益风，扁平插画", "医疗科普风": "清爽专业的医疗科普风", "高端品牌风": "高端极简品牌风，留白与细线",
               "中国传统节日风": "中国传统节日风，祥云灯笼元素", "展会风": "专业展会风，蓝色科技感主视觉", "亲子卡通风": "亲子卡通风，圆润可爱插画",
               "自然田园风": "自然田园风，手绘蔬果与牛皮纸纹理", "校园风": "校园风，黑板与便签元素"}


def _tm(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _ft(x):
    return f"{x // 60:02d}:{x % 60:02d}"


def fix_agenda(ag):
    """make library agendas strictly sequential (reviewers found untagged overlaps); keeps durations."""
    out, prev_end = [], None
    for slot, what in ag:
        m = re.findall(r"(\d{1,2}:\d{2})", slot)
        if len(m) != 2:
            out.append([slot, what])
            continue
        a, b = _tm(m[0]), _tm(m[1])
        if b <= a:
            b = a + 30
        if prev_end is not None and a < prev_end:
            d = b - a
            a, b = prev_end, prev_end + d
        out.append([f"{_ft(a)}—{_ft(b)}", what])
        prev_end = b
    return out


def make_event_spec(e, gid, ref, brand):
    rng = rng_for("event", gid)
    sp = {"id": e["id"], "commercial": e["commercial"]}
    tps = list(e["title_patterns"])
    rng.shuffle(tps)
    tp, start = None, None
    for t in tps:
        d0 = ref["season_fn"](rng, t + " " + e["sub_category"])
        if d0 is not None:
            tp, start = t, d0
            break
    if tp is None:
        tp, start = tps[0], ref["start"]
    ref = dict(ref, start=start)
    pl = B.fict_place(rng)
    NORTH = ["长春市", "沈阳市", "齐齐哈尔市", "呼和浩特市", "银川市", "昌吉回族自治州", "石家庄市", "晋中市", "天津市"]
    outdoor = any(k in json.dumps(e["venue_types"], ensure_ascii=False) for k in ["户外", "草坪", "广场", "露天", "外场"])
    if outdoor and ref["start"].month in (12, 1, 2) and pl["city"] in NORTH:
        pl["city"] = rng.choice(["佛山市", "中山市", "汕头市", "南宁市", "漳州市", "晋江市", "长沙市", "赣州市"])
    city = pl["city"]
    okinds = {"校园": ["学校"], "食品安全": ["市场监管", "街道办事处"], "公益": ["志愿者协会", "街道办事处", "社区居委会"],
              "义卖": ["志愿者协会", "学校"], "检测": ["社区卫生服务中心"], "咨询": ["社区卫生服务中心"], "讲座": ["社区卫生服务中心", "营养学会"],
              "社区": ["街道办事处", "社区居委会"]}
    kinds = next((v for k, v in okinds.items() if k in e["sub_category"]), ["街道办事处", "社区卫生服务中心"])
    org = org_name(rng, rng.choice(kinds), pl)
    short = org.replace(city, "", 1)
    for suf in ("办事处", "社区居民委员会"):
        if short.endswith(suf) and "街道" in short:
            short = short[: short.index("街道") + 2]
    sp["brand"] = brand
    sp["title"] = tp.replace("{brand}", brand).replace("{org}", short + (" " if len(short) > 6 else ""))
    sp["title"] = re.sub(r"\s+", " ", sp["title"]).strip()
    co = B.company_cat(rng, "食品", city=city)
    mall = rng.choice(B.MALLS)
    if e["commercial"]:
        sp["organizer"] = f"{brand}（{co['name']}）" if rng.random() < 0.6 else f"{city.replace('市', '')}{mall}"
    else:
        sp["organizer"] = org
    days = rng.randint(*e["duration_days"])
    start = ref["start"]
    wtxt = json.dumps(e, ensure_ascii=False)
    if "每周三" in wtxt:
        while start.weekday() != 2:
            start = add_days(start, 1)
        days = 1
    elif "周末" in wtxt:
        while start.weekday() != 5:
            start = add_days(start, 1)
        days = min(days, 2)
    import datetime as _dt
    if _dt.date(2027, 2, 4) <= start <= _dt.date(2027, 2, 13) and not any(k in wtxt for k in ("年货", "春节", "新春")):
        start = _dt.date(2027, 2, 20) if "周末" in wtxt else _dt.date(2027, 2, 17)
    end = add_days(start, days - 1)
    sp["start"], sp["end"] = start, end
    sp["end2"], sp["weekday"] = None, None
    sp["hours"] = rng.choice(e["daily_hours"])
    ts = [re.findall(r"(\d{1,2}:\d{2})", a[0]) for a in fix_agenda(copy.deepcopy(e["agenda"]))]
    ts = [t for t in ts if len(t) == 2]
    if ts:
        sp["hours"] = f"{ts[0][0]}—{ts[-1][1]}"
    vt = rng.choice(e["venue_types"])
    road, no = rng.choice(B.ROADS), rng.randint(3, 998)
    if e["commercial"]:
        sp["venue"] = f"{mall}{vt}" if not vt.startswith(mall) else vt
        sp["venue_addr"] = f"{city}{pl['district']}{road}{no}号{mall}"
    else:
        sp["venue"] = f"{pl['street']}{vt}" if "街道" not in vt and "社区" not in vt[:2] else vt
        sp["venue_addr"] = f"{city}{pl['district']}{pl['street']}{road}{no}号"
    sp["venue_addr2"] = None
    sp["agenda"] = copy.deepcopy(e["agenda"])
    sp["agenda"] = fix_agenda(sp["agenda"])
    sp["perks"] = list(e["perks"])
    rng.shuffle(sp["perks"])
    sp["rules"] = list(e["rules"])
    rng.shuffle(sp["rules"])
    sp["hidden"] = e["hidden_condition"]
    sp["hidden_on"] = False
    open_entry = any(k in e["sub_category"] for k in ["市集", "周年庆", "促销", "美食节", "展销", "年货", "开业", "会员日", "快闪"])
    sp["quota"] = None if open_entry else e["quota"]
    sp["open_entry"] = open_entry
    sp["quota2"] = None
    sp["fee"] = e["fee"]
    sp["fee_small"] = None
    sp["speakers"] = None
    if e.get("speaker_roles"):
        names = ["张", "李", "王", "陈", "刘", "周", "吴", "孙", "赵", "徐"]
        sp["speakers"] = [f"{rng.choice(names)}{rng.choice(['晓', '文', '海', '丽', '静', '明', '建', '慧'])}{rng.choice(['华', '宁', '琳', '峰', '敏', '军', '萍', '洁'])}（{r}）" for r in e["speaker_roles"][:2]]
    sp["disclaimer"] = e.get("disclaimer")
    sp["exag"] = e.get("exag_line")
    sp["exag_on"] = None
    sp["phone"] = B.city_phone(rng, city) if not e["commercial"] else rng.choice([B.phone400(rng), B.city_phone(rng, city)])
    needs_booking = any(k in json.dumps(e["rules"] + [e["fee"]], ensure_ascii=False) for k in ["预约", "报名", "邀请函"])
    regs = ["扫描下方二维码报名", "关注公众号回复“报名”", f"电话报名：{sp['phone']}"]
    if not needs_booking:
        regs.append("无需报名，现场签到即可参加")
    sp["reg"] = "无需报名，活动期间营业时间内均可参与" if sp.get("open_entry") else rng.choice(regs)
    if sp["quota"] and days > 1:
        sp["quota_note"] = f"每日限{sp['quota']}名"
    else:
        sp["quota_note"] = None
    sp["style"] = rng.choice(e["visual_styles"])
    sp["motif"] = e["visual_motif"]
    sp["product_hint"] = e.get("product_hint")
    sp["health_related"] = e["health_related"]
    return sp


def event_date_text(sp, alt=False):
    s = sp["start"]
    e = sp["end2"] if (alt and sp["end2"]) else sp["end"]
    if s == e:
        return f"{s.year}年{md_cn(s)}（{sp['weekday'] or weekday_cn(s)}）"
    return f"{s.year}年{md_cn(s)}—{md_cn(e)}" if s.year == e.year else f"{s.year}年{md_cn(s)}—{e.year}年{md_cn(e)}"


def render_event(sp, g, tampers):
    key, subc, _, realism, desc = g["scene"]
    pal = PALETTES[g["palette"]]
    st = EVENT_STYLE.get(sp["style"], sp["style"])
    colour_in_style = any(c in st + sp["motif"] for c in ["色", "配色", "红", "蓝", "绿", "黄", "金", "黑", "牛皮纸", "复古", "烫金", "水墨"])
    pal_txt = "" if colour_in_style else f"；配色：{pal}"
    P = [f"生成一张{g['aspect']}比例的{desc}。{REALISM[realism]}。视觉风格：{st}{pal_txt}；主视觉元素：{sp['motif']}。"]
    top = [f"主办方{Q('主办：' + sp['organizer'])}", f"活动大标题{Q(sp['title'])}"]
    f = sp["fee"]
    if sp.get("open_entry") and f == "免费":
        f = "免费入场"
    if f.startswith("免费") or f.startswith("凭") or f.startswith("按"):
        fee_head = f
    else:
        fee_head = f"费用：{f}"
    unit = "组家庭" if any("家庭" in x for x in sp["rules"] + sp["perks"]) else "名"
    qtxt = sp.get("quota_note") or (f"限{sp['quota']}{unit}" if sp["quota"] else None)
    qtag = f"与{Q(qtxt)}" if qtxt else ""
    top.append(f"标题下方醒目的彩色胶囊标签{Q(fee_head)}" + qtag)
    if sp["exag_on"]:
        top.append(f"标题下方宣传语{Q(sp['exag_on'])}")
    P.append("【标题区】" + "；".join(top) + "。")
    info = [f"活动时间：{event_date_text(sp)} 每日{sp['hours']}" if sp["start"] != sp["end"] else f"活动时间：{event_date_text(sp)} {sp['hours']}",
            f"活动地点：{sp['venue']}", f"地址：{sp['venue_addr']}"]
    if sp["speakers"]:
        info.append("主讲嘉宾：" + "、".join(sp["speakers"]))
    P.append("【基本信息栏（带图标的三到四行）】" + "；".join(Q(x) for x in info) + "。")
    ag = "；".join(Q(f"{a[0]}｜{a[1]}") for a in sp["agenda"])
    P.append(f"【活动流程表（两列表格：时间｜内容）】{ag}。")
    P.append("【活动福利（带序号的卡片）】" + "；".join(Q(x) for x in sp["perks"]) + "。")
    rules = list(sp["rules"])
    if sp["hidden_on"]:
        rules.append(sp["hidden"])
    if sp["fee_small"]:
        rules.append(sp["fee_small"])
    if sp["quota2"]:
        rules.append(f"本次活动{'每日' if sp.get('quota_note') else '共'}开放{sp['quota2']}个名额，报满即止")
    if sp["end2"]:
        rules.append(f"活动期限：{event_date_text(sp, alt=True)}")
    if sp["venue_addr2"]:
        rules.append(f"活动地址：{sp['venue_addr2']}")
    if sp["disclaimer"]:
        rules.append(sp["disclaimer"])
    P.append("【活动须知（海报底部小字，逐条编号）】" + "；".join(Q(x) for x in rules) + "。")
    P.append(f"【页脚】报名方式{Q(sp['reg'])}；咨询电话{Q(sp['phone'])}；右下角二维码图形。")
    if g["artifacts"]:
        P.append("真实感细节：" + "；".join(PHOTO_ARTIFACTS[a] for a in g["artifacts"]) + "。所有文字依然必须清晰可读。")
    P.append(anomaly_note(tampers, "活动宣传设计"))
    P.append(text_rules(False).replace(TEXT_RULE_TABLE, "活动流程表需为行列对齐的完整表格。"))
    return "\n".join(P)


def e_date(sp, level, rng, ctx):
    if level == "subtle":
        if sp["start"] == sp["end"]:
            sp["weekday"] = weekday_cn(add_days(sp["start"], 2))
            return _t("event_date_tamper", "event_weekday", f"活动日期{md_cn(sp['start'])}实为{weekday_cn(sp['start'])}，画面标为（{sp['weekday']}）")
        sp["end2"] = add_days(sp["end"], rng.choice([2, 3, 5]))
        return _t("event_date_tamper", "event_end_date", f"基本信息栏截止{md_cn(sp['end'])}，活动须知写截止{md_cn(sp['end2'])}")
    sp["end2"] = add_days(sp["end"], 30)
    a = sp["agenda"]
    return _t("event_date_tamper", "event_period", f"活动须知中的活动期限被延长一个月至{md_cn(sp['end2'])}，与标题区日期矛盾")


def e_venue(sp, level, rng, ctx):
    a = sp["venue_addr"]
    m = re.search(r"(\d+)号", a)
    if level == "subtle" and m:
        sp["venue_addr2"] = a.replace(m.group(0), f"{int(m.group(1)) + 10}号")
    else:
        alt = B.address(rng)
        sp["venue_addr2"] = f"{alt['city']}{alt['district']}{alt['road']}{alt['no']}号"
    return _t("venue_tamper", "venue_address", f"活动须知中的地址「{sp['venue_addr2']}」与基本信息栏地址「{a}」不一致")


def e_hidden(sp, level, rng, ctx):
    if sp["fee"] != "免费" and level == "subtle":
        return None
    sp["hidden_on"] = True
    if level == "strong" and sp["fee"] == "免费":
        sp["fee_small"] = f"现场需缴纳资料费/材料费¥{rng.choice([49, 69, 99])}，不参与消费不予入场"
        return _t("hidden_fee_condition", "fee", f"标题标“免费”，小字规则加入隐藏付费条件：「{sp['hidden']}」及「{sp['fee_small']}」")
    return _t("hidden_fee_condition", "fee", f"小字规则中加入隐藏付费条件「{sp['hidden']}」")


def e_quota(sp, level, rng, ctx):
    if not sp["quota"]:
        return None
    sp["quota2"] = sp["quota"] + (rng.choice([20, 50]) if level == "subtle" else sp["quota"] * 4)
    return _t("quota_contradiction", "quota", f"标题区限{sp['quota']}名，活动须知写开放{sp['quota2']}个名额")


def e_rule(sp, level, rng, ctx):
    if len(sp["rules"]) < 2:
        return None
    r = sp["rules"].pop(rng.randrange(len(sp["rules"])))
    return _t("promotion_rule_tamper", "rules", f"删除了活动规则「{r}」")


def e_disclaimer(sp, level, rng, ctx):
    if not sp["disclaimer"]:
        return None
    d = sp["disclaimer"]
    sp["disclaimer"] = None
    core = re.sub(r"[，。、；！\s]", "", d)
    grams = {core[i:i + 5] for i in range(max(1, len(core) - 4))}
    sp["rules"] = [x for x in sp["rules"] if not any(g in re.sub(r"[，。、；！\s]", "", x) for g in grams)]
    return _t("warning_deletion", "disclaimer", f"删除了免责/风险提示「{d}」")


def e_exag(sp, level, rng, ctx):
    if not sp["exag"]:
        return None
    sp["exag_on"] = sp["exag"]
    return _t("efficacy_exaggeration", "headline_claim", f"加入违规功效承诺「{sp['exag']}」")


def e_agenda(sp, level, rng, ctx):
    a = sp["agenda"]
    if len(a) < 3:
        return None
    i = rng.randrange(1, len(a))
    t = a[i][0]
    m = re.match(r"(\d{1,2}):(\d{2})\s*[—\-–~至]+\s*(\d{1,2}):(\d{2})", t)
    if not m:
        return None
    pm = re.findall(r"(\d{1,2}:\d{2})", a[i - 1][0])
    if len(pm) != 2:
        return None
    ps, pe = _tm(pm[0]), _tm(pm[1])
    ns = ps + max(10, (pe - ps) // 2)
    ns = ns - ns % 10
    if ns >= pe:
        return None
    new = f"{_ft(ns)}—{m.group(3).zfill(2)}:{m.group(4)}"
    a[i][0] = new
    return _t("agenda_time_conflict", "agenda", f"流程表第{i+1}项时间由{t}改为{new}，与上一项「{a[i-1][0]}」时间段重叠")


def e_fee(sp, level, rng, ctx):
    if sp["fee"] != "免费":
        return None
    sp["fee_small"] = f"报名费¥{rng.choice([29, 39, 59])}/人，活动当日现场缴纳"
    return _t("price_tamper", "fee", f"标题区标“免费”，活动须知写「{sp['fee_small']}」")


EVENT_OPS = {"event_date_tamper": e_date, "venue_tamper": e_venue, "hidden_fee_condition": e_hidden, "quota_contradiction": e_quota,
             "promotion_rule_tamper": e_rule, "warning_deletion": e_disclaimer, "efficacy_exaggeration": e_exag,
             "agenda_time_conflict": e_agenda, "price_tamper": e_fee}
