"""Main generator. Usage: python src/generate.py --groups 50 --out pilot   |   --groups 1000 --out final"""
import argparse
import copy
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from common import rng_for, add_days
import brands as B
import food as F
import promo as PR
import scenes_food as SF
import scenes_other as SO
from visual import PALETTES, PHOTO_ARTIFACTS

import lib_food_a, lib_food_b, lib_food_c, lib_supplement, lib_welfare, lib_event

ARCS = lib_food_a.ARCHETYPES + lib_food_b.ARCHETYPES + lib_food_c.ARCHETYPES
SUPPS = lib_supplement.SUPPLEMENTS
WELF = lib_welfare.WELFARE
EVTS = lib_event.EVENTS

ALLOC_1000 = {"食品标签": 310, "商业广告": 240, "保健品说明": 160, "活动宣传": 150, "公益海报": 140}

# primary-tamper target weights per super category (balanced by deficit)
W_LABEL = {"ingredient_order_tamper": 22, "allergen_deletion": 24, "production_date_tamper": 18, "shelf_life_tamper": 18,
           "efficacy_exaggeration": 9, "nutrition_value_tamper": 8, "claim_nutrition_conflict": 8, "standard_number_tamper": 4,
           "batch_number_tamper": 3, "quantity_tamper": 3, "manufacturer_info_tamper": 3, "storage_condition_tamper": 2,
           "product_attribute_tamper": 2, "target_population_tamper": 1, "warning_deletion": 2}
W_AD = {"price_tamper": 18, "promotion_date_tamper": 15, "efficacy_exaggeration": 14, "allergen_deletion": 12,
        "ingredient_order_tamper": 12, "claim_nutrition_conflict": 7, "production_date_tamper": 9, "shelf_life_tamper": 9,
        "quantity_tamper": 5, "hidden_fee_condition": 4, "quota_contradiction": 3, "promotion_rule_tamper": 3,
        "nutrition_value_tamper": 3, "product_attribute_tamper": 2}
W_SUPP = {"efficacy_exaggeration": 22, "warning_deletion": 14, "target_population_tamper": 10, "allergen_deletion": 12,
          "ingredient_order_tamper": 12, "shelf_life_tamper": 12, "production_date_tamper": 9, "approval_number_tamper": 8,
          "product_attribute_tamper": 5, "function_upgrade": 5, "unsubstantiated_claim": 2, "standard_number_tamper": 2,
          "manufacturer_info_tamper": 2}
W_WELF = {"health_fact_tamper": 25, "misinformation_insertion": 25, "warning_deletion": 15, "event_date_tamper": 12,
          "contact_info_tamper": 12, "quota_contradiction": 5, "source_attribution_tamper": 6}
W_EVT = {"event_date_tamper": 20, "hidden_fee_condition": 18, "venue_tamper": 12, "quota_contradiction": 12,
         "promotion_rule_tamper": 10, "warning_deletion": 10, "efficacy_exaggeration": 8, "agenda_time_conflict": 6, "price_tamper": 6}

FAKE_FUNCS = ["有助于增强免疫力", "有助于改善睡眠", "有助于调节肠道菌群", "缓解视觉疲劳", "有助于维持血糖健康水平", "有助于改善皮肤水份状况"]


class Balancer:
    def __init__(self, weights):
        self.w = weights
        self.c = Counter()
        self.n = 0

    def order(self, rng):
        tot = sum(self.w.values())
        keys = list(self.w)
        rng.shuffle(keys)
        return sorted(keys, key=lambda k: (self.c[k] - self.w[k] / tot * (self.n + 1)))

    def take(self, k):
        self.c[k] += 1
        self.n += 1


def date_pool(rng):
    return dt.date(2026, 9, 20) + dt.timedelta(days=rng.randint(0, 190))


# season windows (verified: 2026 中秋 = 2026-09-25, 2027 春节 = 2027-02-06, via lunardate); dataset window 2026-09-20 .. 2027-03-29
SEASON = [(("中秋", "月饼"), (dt.date(2026, 9, 5), dt.date(2026, 9, 23))), (("国庆",), (dt.date(2026, 9, 26), dt.date(2026, 10, 1))),
          (("年货", "春节", "新春"), (dt.date(2027, 1, 10), dt.date(2027, 2, 3))), (("夏", "冰爽", "暑"), None),
          (("秋冬",), (dt.date(2026, 10, 10), dt.date(2026, 11, 30))), (("秋季", "秋"), (dt.date(2026, 9, 22), dt.date(2026, 11, 20))),
          (("营养周", "营养日"), None), (("冬季",), (dt.date(2026, 12, 1), dt.date(2027, 2, 20)))]


CNY_BLOCK = (dt.date(2027, 2, 4), dt.date(2027, 2, 13))  # 春节假期附近 (2027-02-06 = 正月初一, verified via lunardate)


def _avoid_cny(d, text):
    if CNY_BLOCK[0] <= d <= CNY_BLOCK[1] and not any(k in text for k in ("年货", "春节", "新春")):
        return d + dt.timedelta(days=(CNY_BLOCK[1] - d).days + 3)
    return d


def season_date(rng, text):
    d = _season_date(rng, text)
    return None if d is None else _avoid_cny(d, text)


def _season_date(rng, text):
    for kws, win in SEASON:
        if any(k in text for k in kws):
            if win is None:
                return None  # theme cannot occur inside the dataset window -> caller must not use this text
            a, b = win
            return a + dt.timedelta(days=rng.randint(0, (b - a).days))
    return date_pool(rng)


# ------------------------------------------------------------------ apply plan
OP_ORDER = ["nutrition_value_tamper", "claim_nutrition_conflict", "production_date_tamper", "batch_number_tamper", "shelf_life_tamper"]


def try_apply(builder, ops, plan, level, rng_key, ctx_fn):
    """builder() -> fresh state; ops: name -> fn(state, level, rng, ctx) ; returns (state, tampers) ; skip inapplicable.
    Ops that touch the same fields run in a fixed order so that every tamper_details sentence stays true after all ops."""
    plan = sorted(plan, key=lambda k: OP_ORDER.index(k) if k in OP_ORDER else -1)
    st = builder()
    rng = rng_for(*rng_key)
    ctx = ctx_fn(st)
    out = []
    for name in plan:
        r = ops[name](st, level, rng, ctx)
        if r:
            out.append(r)
    return st, out


def applicable(builder, ops, name, level, key, ctx_fn):
    st = builder()
    ctx = ctx_fn(st)
    return ops[name](st, level, rng_for("probe", *key, name, level), ctx) is not None


def choose_plan(bal, builder, ops, gid, ctx_fn, n_sub=(1, 2), n_str=(2, 3)):
    rng = rng_for("plan", gid)
    order = bal.order(rng)
    prim = None
    for k in order:
        if applicable(builder, ops, k, "subtle", (gid,), ctx_fn) and applicable(builder, ops, k, "strong", (gid,), ctx_fn):
            prim = k
            break
    if prim is None:
        prim = next(k for k in order if applicable(builder, ops, k, "strong", (gid,), ctx_fn))
    bal.take(prim)
    others = [k for k in order if k != prim]
    rng.shuffle(others)
    sub = [prim]
    if rng.random() < 0.4:
        for k in others:
            if applicable(builder, ops, k, "subtle", (gid,), ctx_fn):
                sub.append(k)
                break
    strong = [prim] + [k for k in sub[1:]]
    want = max(rng.choice([2, 3, 3]), len(sub) + 1)
    for k in others:
        if len(strong) >= want:
            break
        if k in strong:
            continue
        if applicable(builder, ops, k, "strong", (gid,), ctx_fn):
            strong.append(k)
    return sub, strong


# ------------------------------------------------------------------ helpers
def density(prompt):
    q = "".join(re.findall("「(.*?)」", prompt, flags=re.S))
    n = len(q)
    if n < 90:
        return "Low"
    if n < 220:
        return "Medium"
    if n < 480:
        return "High"
    return "Very High"


PAIR_ONLY = {"warning_deletion", "promotion_rule_tamper"}


def single_image_detectable(variant, tampers):
    """False when every anomaly in the image is a pure deletion (or an unquantified ingredient swap) that can only be
    found by comparing with the clean pair or with outside knowledge."""
    if variant == "clean":
        return None
    for t in tampers:
        ty, d = t["type"], t["detail"]
        if ty in PAIR_ONLY or (ty == "target_population_tamper" and "删除" in d and "扩大" not in d):
            continue
        if ty == "ingredient_order_tamper" and "添加量" not in d and "原料表中" not in d and "整体重排" not in d:
            continue
        if ty == "manufacturer_info_tamper" and "删除委托" in d:
            continue
        if ty == "allergen_deletion" and "唯一的过敏原提示" in d and "配料表仍含" not in d:
            continue
        return True
    return False


def difficulty(variant, tampers):
    if variant == "clean":
        return "reference"
    if variant == "subtle":
        return "hard" if len(tampers) == 1 else "medium"
    vis = {"efficacy_exaggeration", "price_tamper", "misinformation_insertion", "product_attribute_tamper", "hidden_fee_condition"}
    return "easy" if any(t["type"] in vis for t in tampers) else "medium"


def label_fields(spec, prompt):
    f = ["品名", "产品类型", "配料表", "营养成分表", "净含量", "生产日期", "保质期", "保质期至", "批号", "贮存条件", "生产者信息", "条形码"]
    if spec["allergen_statement"] or spec.get("may_contain"):
        f.append("过敏原信息")
    if spec["standard"] or spec.get("standard2"):
        f.append("执行标准号")
    if spec["claims"]:
        f.append("营养声称")
    if spec.get("function_claim"):
        f.append("营养成分功能声称")
    if spec["selling"] or spec["headline_extra"]:
        f.append("功效/卖点声明")
    if spec.get("license"):
        f.append("生产许可证编号")
    if spec.get("usage"):
        f.append("食用方法")
    if spec.get("population"):
        f.append("适宜人群")
    if spec.get("inkjet_on"):
        f.append("喷码")
    if spec.get("import_info"):
        f.append("原产国/进口商")
    return f


# ------------------------------------------------------------------ group builders
from consistency import container_class
CAR_CLASSES = {"bottle": {"bottle", "barrel"}, "can": {"can"}, "carton": {"carton"}, "giftbox": {"box"}, "back_flat": {"bag", "box"},
               "pair": {"bag", "box", "carton"}, "frozen": {"bag", "box"}, "outer_box": None, "handheld": None, "import": None}


def pack_ok(p, key):
    cls = CAR_CLASSES.get(key)
    if key == "giftbox" and "礼盒" not in p["pack"]:
        return False
    return cls is None or container_class(p["pack"]) in cls


def has_pack(arc, key):
    if key in ("can", "bottle", "carton") and container_class(arc["visual"]) not in CAR_CLASSES[key]:
        return False
    return any(pack_ok(p, key) for p in arc["packages"])


IMPORT_ORIGINS = {"乳制品": ["新西兰", "澳大利亚", "丹麦", "德国"], "饮料": ["泰国", "越南", "马来西亚", "韩国", "日本"],
                  "零食": ["泰国", "马来西亚", "韩国", "日本", "越南"], "烘焙": ["日本", "韩国", "马来西亚", "德国", "比利时"],
                  "蜂产品糖果": ["新西兰", "澳大利亚", "德国", "比利时", "日本"], "冲调谷物": ["澳大利亚", "德国", "马来西亚"],
                  "儿童食品": ["日本", "韩国"]}
NOT_IMPORTED_KW = ["广式", "火锅", "腊", "螺蛳", "汤圆", "水饺", "月饼", "芝麻糊", "藕粉", "粥", "辣条", "魔芋", "肉松", "蛋黄酥", "凉茶", "豆奶", "核桃乳"]


def all_ings(arc):
    """ingredients present in EVERY recipe (a brand head like 椰林 must fit whichever recipe is drawn)."""
    sets = [set(x["n"] for x in r["ing"]) for r in arc["recipes"]]
    return "".join(sorted(set.intersection(*sets))) if sets else ""


def import_ok(arc):
    t = arc["product_type"] + "".join(arc["names"])
    return arc["sub_category"] in IMPORT_ORIGINS and not any(k in t for k in NOT_IMPORTED_KW)


def pick_carrier(arc, rng, gi):
    sc = arc["sub_category"]
    ok = []
    for c in SF.LABEL_CARRIERS:
        k = c[0]
        if not has_pack(arc, k):
            continue
        if k == "import" and not import_ok(arc):
            continue
        if k == "frozen" and not (sc == "冷冻冷藏" or "冷冻" in arc["storage"] or "-18" in arc["storage"]):
            continue
        if k == "giftbox" and sc not in ("烘焙", "零食", "蜂产品糖果", "乳制品", "冲调谷物"):
            continue
        ok += [c] * c[1]
    return rng.choice(ok)


def artifacts_for(realism, rng, carrier_key=None, arc=None, poster=False):
    pool = []
    if poster:
        if realism == "flat":
            return []
        return rng.sample(["phone_shot", "slight_perspective"], rng.choice([1, 2]))
    if realism == "flat":
        return []
    if realism == "studio":
        pool = ["soft_shadow", "slight_perspective"] + (["plastic_glare"] if carrier_key in ("back_flat", "pair", "frozen") and arc and container_class(arc["visual"]) in ("bag", None) else [])
        if carrier_key in ("bottle", "can"):
            pool.append("curved_label")
        if arc and arc["sub_category"] == "冷冻冷藏":
            pool.append("frost")
        return rng.sample(pool, rng.choice([0, 1, 1, 2]))
    pool = ["phone_shot", "slight_perspective", "clutter_bg", "shelf_bg"]
    if carrier_key in ("handheld", "outer_box", "frozen"):
        pool = ["phone_shot", "slight_perspective"] + (["shelf_bg"] if carrier_key == "handheld" else [])
    if carrier_key in ("back_flat", "frozen", "pair", "handheld") and arc and container_class(arc["visual"]) in ("bag", None):
        pool.append("plastic_glare")
    if carrier_key == "frozen" or (arc and arc["sub_category"] == "冷冻冷藏"):
        pool.append("frost")
    if arc and arc["form"] == "liquid" and carrier_key in ("bottle", "can", "handheld") and "冷藏" in arc["storage"]:
        pool.append("condensation")
    out = rng.sample(pool, min(len(pool), rng.choice([1, 2, 3])))
    if carrier_key == "handheld":
        out = ["hand_hold"] + out
    return out


class Gen:
    def __init__(self):
        self.bpool = B.brand_pool()
        self.hpool = B.health_brand_pool()
        self.bi = 0
        self.hi = 0
        self.bal = {"食品标签": Balancer(W_LABEL), "商业广告": Balancer(W_AD), "保健品说明": Balancer(W_SUPP),
                    "公益海报": Balancer(W_WELF), "活动宣传": Balancer(W_EVT)}
        self.cycle = defaultdict(int)
        self.rows = []
        self.used_brands = set()

    def brand(self, health=False):
        if health:
            b = self.hpool[self.hi % len(self.hpool)]
            self.hi += 1
        else:
            b = self.bpool[self.bi % len(self.bpool)]
            self.bi += 1
        return b

    def next_item(self, key, items, gid):
        lst = list(items)
        rng_for("cycle", key).shuffle(lst)
        i = self.cycle[key]
        self.cycle[key] += 1
        return lst[i % len(lst)]

    # ---------------- food label
    def g_label(self, gid):
        rng = rng_for("g", gid)
        arc = self.next_item("arc_label", ARCS, gid)
        car = pick_carrier(arc, rng, gid)
        imported = car[0] == "import"
        brand = B.cat_brand(rng_for("brand", gid), arc["sub_category"], self.used_brands, all_ings(arc))
        ref = {"start": date_pool(rng)}
        g = {"gid": gid, "carrier": car, "aspect": rng.choice(car[2]), "palette": rng.choice(list(PALETTES)),
             "layout": rng.choice(list(SF.LABEL_LAYOUTS)), "artifacts": artifacts_for(car[3], rng, car[0], arc)}

        def build(ink=False):
            s = F.make_food_spec(arc, gid, brand, ref, imported=imported, pack_filter=lambda p: pack_ok(p, car[0]),
                                 unit_label=car[0] in ("bottle", "can", "carton", "handheld", "import"))
            if car[0] == "outer_box":
                s["outer_case"] = True
            s["inkjet_on"] = ink
            s["inkjet_enabled"] = ink
            return s

        ctx_fn = lambda s: {"ref_start": ref["start"]}
        # decide inkjet: probe plan first with inkjet True (so prod-date strong uses 临期改标 story)
        sub, strong = choose_plan(self.bal["食品标签"], lambda: build(True), F.FOOD_OPS, gid, ctx_fn)
        ink = ("production_date_tamper" in sub + strong) or ("batch_number_tamper" in sub + strong) or rng.random() < 0.2
        out = []
        for variant, plan in (("clean", []), ("subtle", sub), ("strong", strong)):
            s, t = try_apply(lambda: build(ink), F.FOOD_OPS, plan, variant if variant != "clean" else "subtle", ("apply", gid, variant), ctx_fn)
            p = SF.render_label(s, g, t)
            meta = {"super_category": "食品标签", "sub_category": f"{arc['sub_category']}标签", "scene_type": car[4].split("，")[0][:40],
                    "carrier": car[0], "product_type": arc["product_type"], "visual_style": ("进口食品中文背标" if imported else "普通包装标签") + f"/{g['palette']}",
                    "layout": f"label_{car[0]}_{g['layout']}", "aspect_ratio": g["aspect"], "realism": car[3],
                    "required_fields": label_fields(s, p), "brand": brand, "product_name": s["name"], "archetype": arc["id"]}
            out.append((variant, meta, t, p))
        return out

    # ---------------- commercial ad
    def g_ad(self, gid):
        rng = rng_for("g", gid)
        scene = self.next_item("ad_scene", SF.AD_SCENES, gid)
        key = scene[0]
        if key == "giftbox_ad":
            arc = self.next_item("arc_gift", [a for a in ARCS if has_pack(a, "giftbox")], gid)
        else:
            arc = self.next_item("arc_ad", ARCS, gid)
        brand = B.cat_brand(rng_for("brand", gid), arc["sub_category"], self.used_brands, all_ings(arc))
        fixed = [f for f in PR.FESTIVALS if f[2]]
        if key == "festival":
            fest = rng.choice(fixed)
        elif key == "flash_mobile":
            fest = next(f for f in PR.FESTIVALS if f[0] == "flash")
        elif key == "launch" or key == "popup":
            fest = next(f for f in PR.FESTIVALS if f[0] == "newlaunch")
        else:
            fest = rng.choice(PR.FESTIVALS)
        if key == "flash_mobile":
            ptype = "秒杀"
        elif key == "giftbox_ad":
            ptype = rng.choice(["组合价", "满减", "直降"])
        else:
            ptype = rng.choice(["直降", "直降", "折扣", "第二件半价", "买二送一", "满减", "会员价", "组合价"])
        prng = rng_for("promo", gid)
        start0 = date_pool(rng)
        store = None
        if key in ("super_poster", "shelf", "leaflet", "glass_door", "standee", "table_card"):
            store = rng.choice(B.MARKETS)
        elif key in ("ecom_detail", "flash_mobile"):
            store = f"{brand}官方旗舰店"
        elif key == "popup":
            store = rng.choice(B.MALLS)
        realism = scene[3]
        pal_pool = {"giftbox_ad": ["black_gold", "deep_navy", "festive_red", "ink_green"], "festival": ["festive_red", "warm_orange", "black_gold", "coral"],
                    "launch": ["gray_minimal", "milk_white", "black_gold", "kraft", "mint"], "popup": ["purple_tech", "coral", "lemon_yellow", "cartoon_multi"],
                    "super_poster": ["tomato_red", "festive_red", "warm_orange", "lemon_yellow", "fresh_blue", "grass_green"],
                    "leaflet": ["tomato_red", "festive_red", "warm_orange", "lemon_yellow", "fresh_blue"],
                    "flash_mobile": ["tomato_red", "coral", "purple_tech", "warm_orange"]}.get(key, list(PALETTES))
        g = {"gid": gid, "ad_scene": scene, "aspect": rng.choice(scene[2]), "palette": rng.choice(pal_pool),
             "artifacts": artifacts_for(realism, rng, None, arc), "store": store}
        g["artifacts"] = [a for a in g["artifacts"] if not (a == "clutter_bg" and key in ("standee", "shelf", "glass_door", "popup"))
                          and not (a in ("frost", "condensation", "plastic_glare") and key != "shelf")]
        if key == "glass_door":
            g["artifacts"] = ["glass_door"] + [a for a in g["artifacts"] if a not in ("hand_hold", "shelf_bg")][:1]
        if key == "shelf":
            g["artifacts"] = ["shelf_bg"] + [a for a in g["artifacts"] if a not in ("shelf_bg", "hand_hold")][:1]

        def build():
            pf = (lambda p: pack_ok(p, "giftbox")) if key == "giftbox_ad" else None
            p0 = PR.make_promo(rng_for("promo", gid), {"price_orig": F.make_food_spec(arc, gid, brand, {"start": start0}, pack_filter=pf)["price_orig"]}, fest, ptype, start0)
            s = F.make_food_spec(arc, gid, brand, {"start": p0["start"]}, pack_filter=pf)
            s["inkjet_on"] = False
            p = PR.make_promo(rng_for("promo", gid), s, fest, ptype, start0)
            if s["expiry"] < p["end"]:   # product would expire during the promotion
                old = s["prod_date"]
                new = add_days(p["start"], -1)
                s["prod_date"] = s["prod_date_true"] = new
                s["expiry"] = F.expiry_of(new, *s["shelf"])
                s["batch"] = s["batch_true"] = F.recode_batch(s["batch"], old, new)
                if s["expiry"] < p["end"]:
                    p["end"] = s["expiry"]
            return {"s": s, "p": p}

        ops = {}
        for k, fn in F.FOOD_OPS.items():
            ops[k] = (lambda fn: lambda st, lv, r, c: fn(st["s"], lv, r, c))(fn)
        for k, fn in PR.PROMO_OPS.items():
            ops[k] = (lambda fn: lambda st, lv, r, c: fn(st["p"], st["s"], lv, r))(fn)
        ops = {k: v for k, v in ops.items() if k in W_AD}
        ctx_fn = lambda st: {"ref_start": st["p"]["start"]}
        sub, strong = choose_plan(self.bal["商业广告"], build, ops, gid, ctx_fn)
        out = []
        for variant, plan in (("clean", []), ("subtle", sub), ("strong", strong)):
            st, t = try_apply(build, ops, plan, variant if variant != "clean" else "subtle", ("apply", gid, variant), ctx_fn)
            p = SF.render_ad(st["s"], st["p"], g, t)
            f = ["品名", "规格", "价格", "活动期限", "活动规则", "配料表", "营养成分表", "生产日期", "保质期", "批号"]
            if st["s"]["allergen_statement"]:
                f.append("过敏原信息")
            if st["s"]["standard"]:
                f.append("执行标准号")
            if st["s"]["selling"] or st["s"]["headline_extra"]:
                f.append("功效/卖点声明")
            if st["p"].get("gift"):
                f.append("赠品与名额")
            meta = {"super_category": "商业广告", "sub_category": scene[1], "scene_type": scene[4][:40], "carrier": key,
                    "product_type": f"{arc['sub_category']}/{arc['product_type']}", "visual_style": SF.AD_STYLE[key].split("：")[0] + f"/{g['palette']}",
                    "layout": f"ad_{key}", "aspect_ratio": g["aspect"], "realism": realism, "required_fields": f, "brand": brand,
                    "product_name": st["s"]["name"], "archetype": arc["id"], "promo_type": ptype, "festival": fest[1]}
            out.append((variant, meta, t, p))
        return out

    # ---------------- supplement
    def g_supp(self, gid):
        rng = rng_for("g", gid)
        s = self.next_item("supp", SUPPS, gid)
        vis = s["visual"]
        def ok_scene(sc):
            if sc[0] == "bottle":
                return "瓶" in vis
            if sc[0] == "sachet":
                return any(w in vis for w in ["袋", "条"]) and "盒" in vis
            if sc[0] == "box_pair":
                return "盒" in vis
            return True
        cands = [sc for sc in SO.SUPP_SCENES if ok_scene(sc)]
        scene = self.next_item("supp_scene_" + str(len(cands)) + cands[0][0], cands, gid)
        brand = self.brand(health=True)
        ref = {"start": date_pool(rng)}
        g = {"gid": gid, "scene": scene, "aspect": rng.choice(scene[2]), "palette": rng.choice(["fresh_blue", "milk_white", "deep_navy", "black_gold", "mint", "warm_orange", "grass_green", "coral", "gray_minimal", "ink_green", "sky_gradient", "berry_pink"]),
             "artifacts": artifacts_for(scene[3], rng, None, None, poster=(scene[0] in ("pharmacy_poster", "ecom", "live_card")))}
        if scene[0] == "leaflet":
            g["artifacts"] = ["paper_crease"]
        build = lambda: SO.make_supp_spec(s, gid, brand, ref)
        FF = {"益生菌与肠道": "有助于调节肠道菌群", "膳食纤维": "有助于润肠通便", "睡眠": "有助于改善睡眠", "叶黄素与护眼": "缓解视觉疲劳",
              "胶原蛋白与美容": "有助于改善皮肤水份状况", "蛋白粉与运动营养": "缓解体力疲劳", "钙与骨骼": "有助于改善骨密度",
              "免疫": "有助于增强免疫力", "维生素矿物质": "有助于增强免疫力", "鱼油与脂类": "有助于维持血脂（胆固醇/甘油三酯）健康水平",
              "植物提取物": "有助于抗氧化", "辅酶Q10": "有助于抗氧化", "中老年营养": "有助于维持血糖健康水平", "儿童营养": "辅助改善记忆",
              "女性营养": "改善缺铁性贫血"}
        ctx_fn = lambda st: {"fake_function": FF.get(s["sub_category"], rng_for("ff", gid).choice(FAKE_FUNCS)), "scene": scene[0]}
        sub, strong = choose_plan(self.bal["保健品说明"], build, SO.SUPP_OPS, gid, ctx_fn)
        out = []
        for variant, plan in (("clean", []), ("subtle", sub), ("strong", strong)):
            st, t = try_apply(build, SO.SUPP_OPS, plan, variant if variant != "clean" else "subtle", ("apply", gid, variant), ctx_fn)
            p = SO.render_supp(st, g, t)
            f = ["品名", "原料/配料", "功效成分含量", "适宜人群", "食用方法", "规格", "贮藏方法", "保质期", "生产日期", "保质期至", "批号", "产品标准号", "生产企业", "许可证编号", "投诉电话", "功效/宣传声明"]
            if st["function"]:
                f.append("保健功能")
            if st["approval"] or st.get("fake_hat"):
                f.append("保健食品标志与批准文号")
            if st["warning"]:
                f.append("警示用语区")
            if st["unsuitable"]:
                f.append("不适宜人群")
            if st["cautions"]:
                f.append("注意事项")
            if st["allergen_statement"]:
                f.append("过敏原信息")
            if st.get("nut"):
                f.append("营养成分表")
            if scene[0] in ("ecom", "live_card", "pharmacy_poster"):
                f.append("价格")
            meta = {"super_category": "保健品说明", "sub_category": s["sub_category"], "scene_type": scene[1], "carrier": scene[0],
                    "product_type": f"{s['reg_type']}/{s['dosage_form']}", "visual_style": ("高端营养品风" if g["palette"] in ("black_gold", "deep_navy", "ink_green") else "保健品包装/医疗科普风") + f"/{g['palette']}",
                    "layout": f"supp_{scene[0]}", "aspect_ratio": g["aspect"], "realism": scene[3], "required_fields": f, "brand": brand,
                    "product_name": st["name"], "archetype": s["id"]}
            out.append((variant, meta, t, p))
        return out

    # ---------------- welfare
    def g_welf(self, gid):
        rng = rng_for("g", gid)
        w = self.next_item("welf", [x for x in WELF if any(season_date(rng_for("s", x["id"]), t) is not None for t in x["titles"])], gid)
        kinds = "".join(w["organizer_types"])
        wsc = [sc for sc in SO.WELF_SCENES if (sc[0] != "school" or "学校" in kinds or "教育" in kinds)
               and (sc[0] != "hospital" or any(k in kinds for k in ["卫生", "医院", "疾病", "妇幼"]))
               and (sc[0] != "metro" or True)]
        scene = self.next_item("welf_scene_" + str(len(wsc)), wsc, gid)
        ref = {"start": date_pool(rng)}
        pal = rng.choice(["fresh_blue", "grass_green", "warm_orange", "mint", "festive_red", "sky_gradient", "lemon_yellow", "cartoon_multi", "coral", "tea_green"])
        arts = artifacts_for(scene[3], rng, poster=True)
        if scene[0] == "board":
            arts = ["board_frame"] + [a for a in arts if a not in ("mall_light",)][:1]
        arts = [a for a in arts if a not in ("shelf_bg", "hand_hold", "plastic_glare")]
        g = {"gid": gid, "scene": scene, "aspect": rng.choice(scene[2]), "palette": pal, "artifacts": arts}
        ref["season_fn"] = season_date
        build = lambda: SO.make_welfare_spec(w, gid, ref, scene[0])
        ctx_fn = lambda st: {}
        sub, strong = choose_plan(self.bal["公益海报"], build, SO.WELF_OPS, gid, ctx_fn)
        out = []
        for variant, plan in (("clean", []), ("subtle", sub), ("strong", strong)):
            st, t = try_apply(build, SO.WELF_OPS, plan, variant if variant != "clean" else "subtle", ("apply", gid, variant), ctx_fn)
            p = SO.render_welfare(st, g, t)
            f = ["主题标题", "主办单位", "科普要点", "咨询电话", "宣传资料编号"]
            if st["warning_on"] and st["key_warning"]:
                f.append("重点风险提示")
            if st["event"]:
                f += ["活动时间", "活动地点", "名额"]
            if st["source_note"]:
                f.append("资料来源")
            meta = {"super_category": "公益海报", "sub_category": w["sub_category"], "scene_type": scene[1], "carrier": scene[0],
                    "product_type": "公益主题/" + w["id"], "visual_style": st["style"] + f"/{pal}", "layout": f"welfare_{scene[0]}",
                    "aspect_ratio": g["aspect"], "realism": scene[3], "required_fields": f, "brand": st["organizer"],
                    "product_name": st["title"], "archetype": w["id"]}
            out.append((variant, meta, t, p))
        return out

    # ---------------- event
    def g_evt(self, gid):
        rng = rng_for("g", gid)
        e = self.next_item("evt", [x for x in EVTS if any(season_date(rng_for("s", x["id"]), t + " " + x["sub_category"]) is not None for t in x["title_patterns"])], gid)
        scene = self.next_item("evt_scene", SO.EVENT_SCENES, gid)
        brand = self.brand(health=("保健" in e["sub_category"] or "健康" in e["sub_category"]) and e["commercial"])
        ref = {"start": date_pool(rng)}
        pal = rng.choice(list(PALETTES))
        arts = artifacts_for(scene[3], rng, poster=True)
        if scene[0] == "board":
            arts = ["board_frame"] + arts[:1]
        if scene[0] == "standee":
            arts = ["easel"] + [a for a in arts if a != "hand_hold"][:1]
        if scene[0] == "flyer":
            arts = ["hand_hold", "paper_crease"]
        g = {"gid": gid, "scene": scene, "aspect": rng.choice(scene[2]), "palette": pal, "artifacts": arts}
        ref["season_fn"] = season_date
        build = lambda: SO.make_event_spec(e, gid, ref, brand)
        ctx_fn = lambda st: {}
        ops = dict(SO.EVENT_OPS)
        sub, strong = choose_plan(self.bal["活动宣传"], build, ops, gid, ctx_fn)
        out = []
        for variant, plan in (("clean", []), ("subtle", sub), ("strong", strong)):
            st, t = try_apply(build, ops, plan, variant if variant != "clean" else "subtle", ("apply", gid, variant), ctx_fn)
            p = SO.render_event(st, g, t)
            f = ["活动名称", "主办方", "活动时间", "活动地点", "地址", "活动流程", "活动福利", "活动须知", "报名方式", "咨询电话", "费用", "名额"]
            if st["speakers"]:
                f.append("主讲嘉宾")
            if st["disclaimer"]:
                f.append("免责/风险提示")
            meta = {"super_category": "活动宣传", "sub_category": e["sub_category"], "scene_type": scene[1], "carrier": scene[0],
                    "product_type": ("商业活动/" if e["commercial"] else "公益活动/") + (e.get("product_hint") or e["id"]),
                    "visual_style": st["style"] + f"/{pal}", "layout": f"event_{scene[0]}", "aspect_ratio": g["aspect"],
                    "realism": scene[3], "required_fields": f, "brand": st["organizer"], "product_name": st["title"], "archetype": e["id"]}
            out.append((variant, meta, t, p))
        return out


def run(n_groups, outdir):
    alloc = {k: round(v * n_groups / 1000) for k, v in ALLOC_1000.items()}
    diff = n_groups - sum(alloc.values())
    alloc["食品标签"] += diff
    gen = Gen()
    fn = {"食品标签": gen.g_label, "商业广告": gen.g_ad, "保健品说明": gen.g_supp, "公益海报": gen.g_welf, "活动宣传": gen.g_evt}
    # interleave categories so IDs are mixed
    seq = []
    for k, v in alloc.items():
        seq += [k] * v
    rng_for("seq", n_groups).shuffle(seq)
    rows = []
    pid = 0
    for gi, cat in enumerate(seq, 1):
        gid = f"G{gi:04d}"
        for variant, meta, t, prompt in fn[cat](gid):
            pid += 1
            row = {"id": f"P{pid:06d}", "group_id": gid, "variant": variant, **{k: meta[k] for k in (
                "super_category", "sub_category", "scene_type", "product_type", "visual_style", "layout", "aspect_ratio")},
                   "text_density": density(prompt), "required_fields": meta["required_fields"],
                   "tamper_types": sorted({x["type"] for x in t}), "tampered_fields": [x["field"] for x in t],
                   "tamper_details": [x["detail"] for x in t], "difficulty": difficulty(variant, t),
                   "single_image_detectable": single_image_detectable(variant, t),
                   "carrier": meta["carrier"], "realism": meta["realism"], "brand_or_organizer": meta["brand"],
                   "product_or_title": meta["product_name"], "source_archetype": meta["archetype"], "prompt": prompt}
            rows.append(row)
    os.makedirs(outdir, exist_ok=True)
    n = len(rows)
    base = os.path.join(outdir, f"poster_prompts_{n}")
    with open(base + ".jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(base + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            rr = dict(r)
            for k in ("required_fields", "tamper_types", "tampered_fields", "tamper_details"):
                rr[k] = "|".join(rr[k])
            w.writerow(rr)
    print(f"wrote {n} rows -> {base}.jsonl/.csv")
    return base


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", type=int, default=50)
    ap.add_argument("--out", default="pilot")
    a = ap.parse_args()
    run(a.groups, a.out)
