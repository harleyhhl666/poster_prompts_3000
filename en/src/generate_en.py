"""English generator. Usage (repo root): python en/src/generate_en.py --groups 334 --out en/final   |  --groups 50 --out en/pilot"""
import argparse
import copy
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_en as C
import eventpsa_en as EP
import food_en as F
import food_ops_en as FO
import geo_en as GE
import lib_event_en, lib_food_en_a, lib_food_en_b, lib_food_en_c, lib_psa_en, lib_supp_en
import lib_geo_en as LG
import lib_names_en as N
import promo_en as P
import scenes_food_en as SF
import scenes_other_en as SO
import supp_en as S
import visual_en as V

HERE = os.path.dirname(os.path.abspath(__file__))
ARCS = lib_food_en_a.ARCHETYPES + lib_food_en_b.ARCHETYPES + lib_food_en_c.ARCHETYPES
SUPPS, EVTS, PSAS = lib_supp_en.SUPPLEMENTS, lib_event_en.EVENTS, lib_psa_en.PSA
F.COUNTRY_NAME.update({k: v["name"] for k, v in LG.COUNTRIES.items()})

CATS = ["Food label", "Commercial ad", "Supplement", "Event", "Public-service poster"]
ALLOC = {"Food label": 104, "Commercial ad": 80, "Supplement": 53, "Event": 50, "Public-service poster": 47}
MARKETS = {"Food label": {"UK": 34, "US": 34, "IE": 24, "MT": 12}, "Supplement": {"US": 27, "UK": 14, "IE": 8, "MT": 4},
           "Commercial ad": {"UK": 16, "IE": 8, "US": 20, "EU": 36}, "Event": {"UK": 9, "IE": 5, "US": 10, "CA": 6, "EU": 20},
           "Public-service poster": {"UK": 9, "IE": 5, "US": 10, "CA": 5, "EU": 18}}
W = {"Food label": {"ingredient_order_tamper": 22, "allergen_deletion": 24, "production_date_tamper": 18, "shelf_life_tamper": 18,
                    "efficacy_exaggeration": 9, "nutrition_value_tamper": 8, "claim_nutrition_conflict": 8, "batch_number_tamper": 5,
                    "quantity_tamper": 3, "manufacturer_info_tamper": 5, "storage_condition_tamper": 2, "product_attribute_tamper": 2,
                    "target_population_tamper": 1, "warning_deletion": 2},
     "Commercial ad": {"price_tamper": 18, "promotion_date_tamper": 15, "efficacy_exaggeration": 14, "allergen_deletion": 12,
                       "ingredient_order_tamper": 12, "claim_nutrition_conflict": 7, "production_date_tamper": 9, "shelf_life_tamper": 9,
                       "quantity_tamper": 5, "hidden_fee_condition": 4, "quota_contradiction": 3, "promotion_rule_tamper": 3,
                       "nutrition_value_tamper": 3, "product_attribute_tamper": 2},
     "Supplement": {"efficacy_exaggeration": 22, "warning_deletion": 14, "target_population_tamper": 10, "allergen_deletion": 12,
                    "ingredient_order_tamper": 12, "shelf_life_tamper": 12, "production_date_tamper": 9, "regulatory_status_tamper": 8,
                    "product_attribute_tamper": 5, "function_upgrade": 5, "unsubstantiated_claim": 2, "nutrition_value_tamper": 2,
                    "manufacturer_info_tamper": 2},
     "Public-service poster": {"health_fact_tamper": 25, "misinformation_insertion": 25, "warning_deletion": 15, "event_date_tamper": 12,
                               "contact_info_tamper": 12, "quota_contradiction": 5, "source_attribution_tamper": 6},
     "Event": {"event_date_tamper": 20, "hidden_fee_condition": 18, "venue_tamper": 12, "quota_contradiction": 12,
               "promotion_rule_tamper": 10, "warning_deletion": 10, "efficacy_exaggeration": 8, "agenda_time_conflict": 6, "price_tamper": 6}}
OP_ORDER = ["nutrition_value_tamper", "claim_nutrition_conflict", "production_date_tamper", "batch_number_tamper", "shelf_life_tamper"]
W0, W1 = dt.date(2026, 10, 1), dt.date(2027, 4, 30)


class Balancer:
    def __init__(self, w):
        self.w, self.c, self.n = w, Counter(), 0

    def order(self, rng):
        tot = sum(self.w.values())
        ks = list(self.w)
        rng.shuffle(ks)
        return sorted(ks, key=lambda k: self.c[k] - self.w[k] / tot * (self.n + 1))

    def take(self, k):
        self.c[k] += 1
        self.n += 1


def try_apply(builder, ops, plan, level, key):
    plan = sorted(plan, key=lambda k: OP_ORDER.index(k) if k in OP_ORDER else -1)
    st, ctx = builder()
    rng = C.rng_for(*key)
    out = []
    for nm in plan:
        # operators may mutate the spec before discovering they are not applicable; roll back so a skipped
        # operator cannot leave an unlisted edit behind (review round 4: sugars cut with no tamper_details entry)
        bak = copy.deepcopy(st)
        r = ops[nm](st, level, rng, ctx)
        if r:
            out.append(r)
        else:
            st.clear()
            st.update(bak)
    return st, out


def applicable(builder, ops, nm, level, gid):
    st, ctx = builder()
    return ops[nm](st, level, C.rng_for("probe", gid, nm, level), ctx) is not None


def choose_plan(bal, builder, ops, gid):
    rng = C.rng_for("plan", gid)
    order = bal.order(rng)
    prim = next((k for k in order if applicable(builder, ops, k, "subtle", gid) and applicable(builder, ops, k, "strong", gid)), None)
    if prim is None:
        prim = next(k for k in order if applicable(builder, ops, k, "strong", gid))
    bal.take(prim)
    others = [k for k in order if k != prim]
    rng.shuffle(others)
    sub = [prim]
    if rng.random() < 0.4:
        for k in others:
            if applicable(builder, ops, k, "subtle", gid):
                sub.append(k)
                break
    strong = list(sub)
    want = max(rng.choice([2, 3, 3]), len(sub) + 1)
    for k in others:
        if len(strong) >= want:
            break
        if k not in strong and applicable(builder, ops, k, "strong", gid):
            strong.append(k)
    return sub, strong


def density(prompt):
    n = len("".join(re.findall("「(.*?)」", prompt, flags=re.S)))
    return "Low" if n < 200 else "Medium" if n < 500 else "High" if n < 1200 else "Very High"


PAIR_ONLY = {"warning_deletion", "promotion_rule_tamper"}
US_SPELL = [("flavouring", "flavoring"), ("Flavouring", "Flavoring"), ("flavour", "flavor"), ("Flavour", "Flavor"), ("colour", "color"),
            ("Colour", "Color"), ("fibre", "fiber"), ("Fibre", "Fiber"), ("yoghurt", "yogurt"), ("pasteurised", "pasteurized"),
            ("Pasteurised", "Pasteurized"), ("glycerol", "glycerin"), ("GLYCEROL", "GLYCERIN"), ("favourite", "favorite"),
            ("sulphite", "sulfite"), ("SULPHITE", "SULFITE"), ("caramelised", "caramelized"), ("stabiliser", "stabilizer"),
            ("Stabiliser", "Stabilizer"), ("STABILISER", "STABILIZER"), ("emulsifiers", "emulsifiers"), ("centre", "center"),
            ("Centre", "Center"), ("at the till", "at checkout"), ("the till", "checkout"), ("fish fingers", "fish sticks"),
            ("Fish Fingers", "Fish Sticks"), ("prawns", "shrimp"), ("prawn", "shrimp"), ("teatime", "snack time"),
            ("programme", "program"), ("Programme", "Program"), ("organis", "organiz"), ("Organis", "Organiz"), ("litre", "liter"),
            ("FLAVOURING", "FLAVORING"), ("FLAVOUR", "FLAVOR"), ("COLOUR", "COLOR"), ("FIBRE", "FIBER"), ("PASTEURISED", "PASTEURIZED"),
            ("YOGHURT", "YOGURT"), ("RAPESEED OIL", "CANOLA OIL"), ("rapeseed oil", "canola oil"), ("Rapeseed oil", "Canola oil"),
            ("haemochromatosis", "hemochromatosis"), ("standardised", "standardized"), ("Standardised", "Standardized"),
            ("speciality", "specialty"), ("Speciality", "Specialty"), ("linseed", "flaxseed"), ("Linseed", "Flaxseed"),
            ("LINSEED", "FLAXSEED"), ("skimmed milk", "skim milk"), ("Skimmed milk", "Skim milk"), ("SKIMMED MILK", "SKIM MILK"),
            ("Soya", "Soy"), ("soya", "soy"), ("SOYA", "SOY"), ("Unflavoured", "Unflavored"), ("unflavoured", "unflavored"),
            ("flavoured", "flavored"), ("Flavoured", "Flavored"), ("FLAVOURED", "FLAVORED"), ("aluminium", "aluminum"),
            ("Village Hall", "Community Hall"), ("neighbour", "neighbor"), ("Neighbour", "Neighbor")]


NA_WORDS = [("wellies", "rain boots"), ("Wellies", "Rain boots"), ("fancy dress", "costume"), ("Fancy dress", "Costume"),
            ("traybakes", "sheet-pan bakes"), ("traybake", "sheet-pan bake"), ("your GP", "your doctor"), ("a GP", "a doctor"),
            ("GP or", "doctor or"), ("Autumn", "Fall"), ("under a fiver", "under $5"), ("every penny", "every cent"),
            ("Places: ", "Spots: "), ("Co-operative", "Co-op"), ("high street", "main street"), ("High Street", "Main Street"),
            ("Freephone", "Toll-free"), ("freephone", "toll-free"), ("Mum", "Mom"), ("mum", "mom"), ("queue", "line"),
            ("Queue", "Line"), ("car park", "parking lot"), ("Car park", "Parking lot"), ("diary", "calendar"), ("fortnight", "two weeks")]
US_ONLY = [("Crisps", "Chips"), ("crisps", "chips"), ("CRISPS", "CHIPS"), ("PRAWN", "SHRIMP"), ("Prawn", "Shrimp")]


def na_wording(p, c):
    for a, b in NA_WORDS + (US_ONLY if c == "US" else []):
        p = re.sub(r"(?<![A-Za-z])" + re.escape(a) + r"(?![a-z])", b, p)
    p = re.sub(r"\b(\d+) places\b", r"\1 spots", p)
    return us_spelling(p) if c == "US" else p


def us_spelling(p):
    for a, b in US_SPELL:
        p = re.sub(r"\b" + re.escape(a), b, p) if a[0].isalpha() else p.replace(a, b)
    return p


def sid(variant, tampers):
    if variant == "clean":
        return None
    for t in tampers:
        if "sid" in t:
            if t["sid"]:
                return True
            continue
        if t["type"] in PAIR_ONLY or (t["type"] == "target_population_tamper" and "deleted" in t["detail"]):
            continue
        return True
    return False


def difficulty(variant, tampers):
    if variant == "clean":
        return "reference"
    if variant == "subtle":
        return "hard" if len(tampers) == 1 else "medium"
    vis = {"efficacy_exaggeration", "price_tamper", "misinformation_insertion", "product_attribute_tamper", "hidden_fee_condition", "regulatory_status_tamper"}
    return "easy" if any(t["type"] in vis for t in tampers) else "medium"


CALM = ["fresh_blue", "meadow_green", "sage", "mint", "minimal_grey", "sky_gradient", "nordic", "coral", "lemon", "cream", "pastel"]


def palette(cat, rng, d=None):
    """festive palette only in the Christmas window; loud palettes not for public-information posters"""
    keys = list(V.PALETTES)
    if not (d and dt.date(2026, 11, 15) <= d <= dt.date(2026, 12, 31)):
        keys.remove("festive_red")
    if cat in ("psa", "supp"):
        keys = [k for k in keys if k in CALM]
    return rng.choice(keys)


HOLIDAY_END = {"Halloween treats": dt.date(2026, 10, 31), "Thanksgiving savings": C.nth_weekday(2026, 11, 3, 4),
               "Black Friday deals": dt.date(2026, 11, 30), "Christmas savings": dt.date(2026, 12, 24),
               "Valentine's treats": dt.date(2027, 2, 14), "Pancake Day offers": C.add_days(C.easter(2027), -47),
               "St Patrick's Day savings": dt.date(2027, 3, 17), "Easter savings": C.easter(2027), "New Year offers": dt.date(2027, 1, 6)}


def _fact_regions():
    out = {}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "refs", "facts_whitelist.md"), encoding="utf-8") as f:
        for l in f:
            c = [x.strip() for x in l.split("|")]
            if len(c) > 4 and re.match(r"^[a-z0-9_]+$", c[1]) and c[1] != "fact_id":
                out[c[1]] = [x.strip() for x in c[3].split(",")]
    return out


FACT_REG = _fact_regions()


def baby_food(a):
    return bool(a.get("population")) and bool(re.search(r"month", a["population"], re.I))


def eu_countries():
    return sorted(c for c, v in LG.COUNTRIES.items() if v["region"] == "EU" and v["lang_context"] == "international")


def artifacts(realism, rng, carrier, sp=None):
    if realism == "flat":
        return []
    if realism == "studio":
        pool = ["soft_shadow", "slight_perspective"] + (["curved_label"] if carrier in ("bottle_wrap", "can_tin", "bottle_label") else [])
        return rng.sample(pool, rng.choice([0, 1, 1, 2]))
    pool = ["phone_shot", "slight_perspective"]
    if carrier in ("freezer",):
        pool += ["frost", "plastic_glare"]
    if carrier in ("handheld",):
        pool += ["shelf_bg"]
    if carrier in ("noticeboard",):
        pool += ["pinned", "glass_reflection"]
    if carrier in ("window", "a_frame"):
        pool += ["glass_reflection"] if carrier == "window" else []
    out = rng.sample(pool, min(len(pool), rng.choice([1, 2])))
    if carrier == "handheld":
        out = ["hand_hold"] + out
    return out


def ad_theme(d, region, rng):
    E = C.easter(2027)
    T = []
    if dt.date(2026, 10, 20) <= d <= dt.date(2026, 10, 31): T.append("Halloween treats")
    if region == "US" and dt.date(2026, 11, 9) <= d <= dt.date(2026, 11, 26): T.append("Thanksgiving savings")
    if dt.date(2026, 11, 23) <= d <= dt.date(2026, 11, 30): T.append("Black Friday deals")
    if dt.date(2026, 12, 1) <= d <= dt.date(2026, 12, 24): T.append("Christmas savings")
    if dt.date(2026, 12, 27) <= d <= dt.date(2027, 1, 6): T.append("New Year offers")
    if dt.date(2027, 1, 7) <= d <= dt.date(2027, 1, 31): T.append("January savings")
    if dt.date(2027, 2, 1) <= d <= dt.date(2027, 2, 14): T.append("Valentine's treats")
    if region in ("UK", "IE") and C.add_days(E, -53) <= d <= C.add_days(E, -47): T.append("Pancake Day offers")
    if region in ("IE", "UK", "US") and dt.date(2027, 3, 10) <= d <= dt.date(2027, 3, 17): T.append("St Patrick's Day savings")
    if C.add_days(E, -18) <= d <= E: T.append("Easter savings")
    if d >= dt.date(2027, 3, 29): T.append("Spring savings")
    if d <= dt.date(2026, 11, 22): T.append("Autumn savings")
    T.append("This week's offers")
    return rng.choice(T)


FOOD_TAILS_OK = {"", "& Co.", "Larder", "Pantry", "Provisions", "Table", "Fine Foods", "& Sons", "Hearth", "Kitchen Co."}
HEALTH_TAILS_BAD = {"Pharmaceuticals", "Clinic", "Medica", "Remedies", "Healthcare", "Apothecary", "Nutraceuticals", "Probiotix", "Botanicals"}
SEASONAL_KW = {"christmas": ["panettone", "mince", "stollen", "gingerbread", "lebkuchen", "christmas"], "easter": ["hot_cross", "easter"]}


def arc_season(a):
    for k, kws in SEASONAL_KW.items():
        if any(w in a["id"] for w in kws):
            return k
    return None


class Gen:
    def __init__(self):
        rng = C.rng_for("brands")
        bl = [b.lower() for b in N.REAL_BRAND_BLACKLIST]
        # neutral tails only: category words ('Dairy', 'Roastery', 'Orchards'...) clash with arbitrary products, and
        # drug-like words ('Pharmaceuticals', 'Clinic', 'Medica') would blur the regulatory-status tamper.
        ft = [t for t in N.FOOD_BRAND_TAILS if t in FOOD_TAILS_OK]
        ht = [t for t in N.HEALTH_BRAND_TAILS if t not in HEALTH_TAILS_BAD]
        self.fb = GE.brand_pool(N.FOOD_BRAND_HEADS, ft, bl, rng, per_head=2)
        self.hb = GE.brand_pool(N.HEALTH_BRAND_HEADS, ht, bl, rng, per_head=2)
        self.fi = self.hi = 0
        self.bal = {c: Balancer(W[c]) for c in CATS}
        self.use = defaultdict(Counter)
        self.eu_use = Counter()
        self.rows = []
        with open(os.path.join(HERE, "..", "refs", "facts_whitelist.md"), encoding="utf-8") as fh:
            self.fact_src = {m.group(1): m.group(2).strip() for m in re.finditer(r"^\| ([a-z0-9_]+) \|[^|]*\|[^|]*\| ([^|]+) \|", fh.read(), flags=re.M)}

    def brand(self, health=False):
        if health:
            self.hi += 1
            return self.hb[(self.hi - 1) % len(self.hb)]
        self.fi += 1
        return self.fb[(self.fi - 1) % len(self.fb)]

    def eu_country(self, rng):
        cs = eu_countries()
        rng.shuffle(cs)
        c = min(cs, key=lambda x: self.eu_use[x])
        self.eu_use[c] += 1
        return c

    def pick(self, cat, items, ok, rng):
        cand = [x for x in items if ok(x)]
        rng.shuffle(cand)
        x = min(cand, key=lambda a: self.use[cat][a["id"]])
        self.use[cat][x["id"]] += 1
        return x

    def emit(self, gid, cat, meta, renders, plans):
        for variant in ("clean", "subtle", "strong"):
            prompt, tampers = renders[variant]
            row = dict(meta)
            if meta["country"] in ("US", "CA"):
                prompt = na_wording(prompt, meta["country"])
                tampers = [dict(t, detail=na_wording(t["detail"], meta["country"])) for t in tampers]
            row.update({"group_id": gid, "variant": variant, "super_category": cat, "text_density": density(prompt),
                        "tamper_types": [t["type"] for t in tampers], "tampered_fields": sorted({t["field"] for t in tampers}),
                        "tamper_details": [t["detail"] for t in tampers], "difficulty": difficulty(variant, tampers),
                        "single_image_detectable": sid(variant, tampers), "lang": "en", "prompt": prompt})
            self.rows.append(row)

    def variants(self, builder, ops, gid, cat, render):
        sub, strong = choose_plan(self.bal[cat], builder, ops, gid)
        out = {}
        st, _ = builder()
        out["clean"] = (render(st, "clean", []), [])
        for lvl, plan in (("subtle", sub), ("strong", strong)):
            st, tam = try_apply(builder, ops, plan, lvl, (gid, lvl))
            if lvl == "strong" and len(tam) <= len(out["subtle"][1]):
                # an op that was applicable alone can become inapplicable after another op ran: add one more that works
                for k in self.bal[cat].order(C.rng_for("fallback", gid)):
                    if k in plan:
                        continue
                    st2, tam2 = try_apply(builder, ops, plan + [k], lvl, (gid, lvl))
                    if len(tam2) > len(out["subtle"][1]):
                        st, tam = st2, tam2
                        break
            out[lvl] = (render(st, lvl, tam), tam)
        return out


# ====================================================================== group builders
def us_ok(a):
    """US: sulfiting agents are not permitted in meat (21 CFR 182.3766 et seq. exclude meats) -> skip such recipes for US"""
    return not (a["sub_category"] == "Meat, fish & deli" and any("sulphite" in i["n"].lower() or "sulfite" in i["n"].lower() or "metabisul" in i["n"].lower()
                                                               for r in a["recipes"] for i in r["ing"]))


def is_frozen(a):
    s = a["storage"].lower()
    return "{freezer}" in a["storage"] and ("keep frozen" in s or "store frozen" in s or "frozen" in a["legal_name"].lower()) or "keep frozen" in s


def label_group(gen, gid, market, rng):
    # US baby foods need the infant Nutrition Facts format (not modelled) -> no US baby-food labels
    arc = gen.pick("label", ARCS, lambda a: market in a.get("markets", ["UK", "IE", "MT", "US"]) and (market != "US" or (us_ok(a) and not baby_food(a))), rng)
    seas = arc_season(arc)
    if seas == "christmas":
        ref = dt.date(2026, 11, 10) + dt.timedelta(days=rng.randint(0, 42))
    elif seas == "easter":
        ref = dt.date(2027, 3, 1) + dt.timedelta(days=rng.randint(0, 26))
    else:
        ref = W0 + dt.timedelta(days=rng.randint(0, (W1 - W0).days))
    packs = {p["pack"] for p in arc["packages"] if F.pack_in_visual(p["pack"], arc["visual"])} or {p["pack"] for p in arc["packages"]}
    frozen = is_frozen(arc)
    ok = []
    for key, w in SF.LABEL_CARRIERS:
        need = {"bottle_wrap": {"bottle", "jar"}, "can_tin": {"can", "tin"}, "carton_side": {"carton", "box"}}.get(key)
        if need is not None and not (packs & need):
            continue
        if key == "freezer" and not frozen:
            continue
        ok += [key] * w
    car = rng.choice(ok)
    need = {"bottle_wrap": {"bottle", "jar"}, "can_tin": {"can", "tin"}, "carton_side": {"carton", "box"}}.get(car)
    pf = (lambda p: p["pack"] in need) if need else None
    brand = gen.brand()
    realism = {"back_flat": rng.choice(["flat", "studio"]), "front_back": rng.choice(["flat", "studio"]), "freezer": "phone",
               "handheld": "phone"}.get(car, "studio")
    g = {"carrier": car, "ar": rng.choice(SF.CARRIER_DESC[car][1]), "realism": realism, "style": rng.choice(V.STYLES["label"]),
         "palette": palette("label", rng, ref), "layout": rng.choice(["two-column information layout", "single-column information layout",
                                                                         "three-column layout with the nutrition table on the right",
                                                                         "nutrition-table-led layout"])}
    g["artifacts"] = artifacts(realism, rng, car)

    def builder():
        sp = F.build(arc, gid, market, brand, ref, C.rng_for("spec", gid), GE, pf)
        return sp, {"ref": ref, "inkjet": True}
    sp0, _ = builder()
    rf = ["Product name", "Legal name", "Ingredients", "Nutrition table", "Net quantity", "Production date", sp0["date_kind"], "Shelf life",
          "Lot code", "Inkjet code", "Storage", "Producer details", "Customer care", "Barcode", "Origin"]
    if any(i["a"] for i in sp0["ings"]) or sp0["may"]:
        rf.insert(3, "Allergen information")
    if sp0["claims"]:
        rf.append("Nutrition claims")
    if sp0["health_claim"]:
        rf.append("Health claim")
    if sp0["importer"]:
        rf.append("Importer")
    if sp0["population"]:
        rf.append("Suitability")
    meta = {"sub_category": arc["sub_category"], "country": market, "region": LG.COUNTRIES[market]["region"],
            "scene_type": SF.CARRIER_DESC[car][0].format(pack=sp0["pack"]["pack"]), "product_type": arc["legal_name"],
            "visual_style": "%s/%s" % (g["style"], g["palette"]), "layout": g["layout"], "aspect_ratio": g["ar"], "carrier": car,
            "realism": realism, "brand_or_organizer": brand, "product_or_title": sp0["name"], "source_archetype": arc["id"],
            "required_fields": rf}
    return meta, builder, FO.FOOD_OPS, (lambda st, v, t: SF.label_prompt(st, g, v, t))


def _wrap_food(k):
    return lambda st, l, r, c: FO.FOOD_OPS[k](st["sp"], l, r, c)


def _wrap_promo(k):
    return lambda st, l, r, c: P.PROMO_OPS[k](st["p"], st["sp"], l, r, c)


AD_OPS = {k: _wrap_food(k) for k in FO.FOOD_OPS}
AD_OPS.update({k: _wrap_promo(k) for k in P.PROMO_OPS})


def ad_group(gen, gid, region, rng):
    country = region if region in ("UK", "IE", "US") else gen.eu_country(rng)
    rk = "US" if country == "US" else ("UK" if country == "UK" else ("IE" if country == "IE" else "EU"))
    fit = (lambda a: "US" in a.get("markets", ["US"]) and us_ok(a) and not baby_food(a)) if country == "US" else (lambda a: any(m in a.get("markets", ["UK"]) for m in ("UK", "IE", "MT")))
    arc = gen.pick("ad", ARCS, fit, rng)
    seas = arc_season(arc)
    if seas == "christmas":
        start = dt.date(2026, 11, 20) + dt.timedelta(days=rng.randint(0, 25))
    elif seas == "easter":
        start = dt.date(2027, 3, 8) + dt.timedelta(days=rng.randint(0, 14))
    else:
        start = W0 + dt.timedelta(days=rng.randint(0, (W1 - W0).days - 14))
    days = rng.choice([3, 4, 7, 7, 10, 14])
    theme = ad_theme(start, rk if country != "US" else "US", rng)
    sweet = re.search(r"confection|snack|bakery|biscuit|spread|dessert|dairy|breakfast|chocolate|sweet", arc["sub_category"], re.I)
    if theme in ("Halloween treats", "Valentine's treats", "Pancake Day offers", "Easter savings") and not sweet:
        theme = "Special offers"
    if theme == "This week's offers" and days > 7:
        theme = "Special offers"
    if theme in HOLIDAY_END and HOLIDAY_END[theme] >= start:
        days = (HOLIDAY_END[theme] - start).days + 1   # a holiday offer runs up to the holiday itself
    cur = LG.COUNTRIES[country]["currency"]
    cty = GE.city(country, rng)
    car, cdesc, ars, realism = rng.choice(SF.AD_CARRIERS)
    retailer = rng.choice([r for r in N.RETAILERS[rk] if not re.search(r"pharm|farmac|chemist|apothe|drug|aptiek|lékárna|apteka", r, re.I)])
    brand = gen.brand()
    g = {"carrier": car, "carrier_desc": cdesc, "ar": rng.choice(ars), "realism": realism, "style": rng.choice(V.STYLES["ad"]),
         "palette": palette("ad", rng, start), "city": cty["city"], "retailer": retailer, "theme": theme,
         "en_context": GE.en_context(country, rng, cty)}
    g["artifacts"] = artifacts(realism, rng, car)

    def builder():
        sp = F.build(arc, gid, country, brand, start, C.rng_for("spec", gid), GE)
        sp["price_eur"] = sp["pack"]["price_eur"]
        p = P.make(C.rng_for("promo", gid), sp, rk, cur, start, days, country == "US")
        return {"sp": sp, "p": p}, {"ref": start, "inkjet": False}
    st0, _ = builder()
    sp0 = st0["sp"]
    rf = ["Retailer", "Product name", "Price", "Offer period", "Offer rules", "Ingredients", "Nutrition table", "Production date",
          sp0["date_kind"], "Shelf life", "Lot code", "Storage", "Producer details"]
    if any(i["a"] for i in sp0["ings"]):
        rf.append("Allergen information")
    if sp0["claims"]:
        rf.append("Nutrition claims")
    meta = {"sub_category": car, "country": country, "region": LG.COUNTRIES[country]["region"],
            "scene_type": cdesc.format(city=cty["city"], retailer=retailer), "product_type": arc["legal_name"],
            "visual_style": "%s/%s" % (g["style"], g["palette"]), "layout": "ad_" + car, "aspect_ratio": g["ar"], "carrier": car,
            "realism": realism, "brand_or_organizer": brand, "product_or_title": sp0["name"], "source_archetype": arc["id"],
            "required_fields": rf}
    return meta, builder, AD_OPS, (lambda st, v, t: SF.ad_prompt(st["sp"], st["p"], g, v, t))


def supp_group(gen, gid, market, rng):
    reg = "US" if market == "US" else "EU"
    s = gen.pick("supp", SUPPS, lambda x: reg in x["regimes"], rng)
    ref = W0 + dt.timedelta(days=rng.randint(0, (W1 - W0).days))
    car, cdesc, ars, realism = rng.choice(SO.SUPP_CARRIERS)
    cur = LG.COUNTRIES[market]["currency"]
    cty = GE.city(market, rng)
    brand = gen.brand(health=True)
    pr = C.eur_to(rng.uniform(*s["price_eur"]), cur, rng)
    g = {"carrier": car, "carrier_desc": cdesc, "ar": rng.choice(ars), "realism": realism, "style": rng.choice(V.STYLES["supp"]),
         "palette": palette("supp", rng, ref), "city": cty["city"], "en_context": None,
         "price_lines": [C.money(pr, cur), "Subscribe and save 10%: " + C.money(C.money_round(pr * 0.9, cur), cur)]}
    g["artifacts"] = artifacts(realism, rng, car)

    def builder():
        sp = S.build(s, gid, market, brand, ref, C.rng_for("spec", gid), GE)
        return sp, {"ref": ref, "country_name": GE.country_name}
    sp0, _ = builder()
    rf = ["Product name", "Product category statement", "Facts table", "Ingredients", "Directions", "Warnings", "Suitability",
          "Date of manufacture", "Expiry/best before", "Shelf life", "Lot code", "Inkjet code", "Manufacturer", "Customer care", "Barcode"]
    if sp0["claims"]:
        rf.append("Claims")
    if sp0["disclaimer"]:
        rf.append("FDA disclaimer")
    if S.allergen_line(sp0):
        rf.append("Allergen information")
    if car in ("ecommerce", "pharmacy_poster", "social_card"):
        rf.append("Price")
    meta = {"sub_category": s["sub_category"], "country": market, "region": LG.COUNTRIES[market]["region"],
            "scene_type": cdesc.format(pack=s["pack"], form=s["form"], city=cty["city"]), "product_type": "%s (%s)" % (sp0["label_type"], s["form"]),
            "visual_style": "%s/%s" % (g["style"], g["palette"]), "layout": "supp_" + car, "aspect_ratio": g["ar"], "carrier": car,
            "realism": realism, "brand_or_organizer": brand, "product_or_title": sp0["name"], "source_archetype": s["id"], "required_fields": rf}
    return meta, builder, S.SUPP_OPS, (lambda st, v, t: SO.supp_prompt(st, g, v, t))


def event_group(gen, gid, region, rng):
    country = region if region in ("UK", "IE", "US", "CA") else gen.eu_country(rng)
    e = gen.pick("event", EVTS, lambda x: region in x["regions"], rng)
    cur = LG.COUNTRIES[country]["currency"]
    brand = gen.brand() if e["commercial"] else ""
    car, cdesc, ars, realism = rng.choice(SO.EVENT_CARRIERS)
    g = {"carrier": car, "carrier_desc": cdesc, "ar": rng.choice(ars), "realism": realism, "style": rng.choice(e["visual_styles"] + V.STYLES["event"][:2]),
         "palette": palette("event", rng, EP.SEASON[e["season"]][0] if e["season"] in ("christmas", "christmas_market") else None)}
    g["artifacts"] = artifacts(realism, rng, car)

    def builder():
        return EP.build_event(e, gid, country, C.rng_for("ev", gid), brand, cur, country in ("US", "CA")), {}
    sp0, _ = builder()
    rf = ["Organiser", "Title", "Dates", "Opening hours", "Venue", "Address", "Programme", "Perks", "Rules", "Places", "Fee", "Contact"]
    if sp0["disclaimer"]:
        rf.append("Disclaimer")
    if sp0["speakers"]:
        rf.append("Speakers")
    meta = {"sub_category": e["sub_category"], "country": country, "region": LG.COUNTRIES[country]["region"],
            "scene_type": cdesc.format(city=sp0["city"]["city"]), "product_type": e["product_hint"] or "",
            "visual_style": "%s/%s" % (g["style"], g["palette"]), "layout": "event_" + car, "aspect_ratio": g["ar"], "carrier": car,
            "realism": realism, "brand_or_organizer": sp0["organizer"], "product_or_title": sp0["title"], "source_archetype": e["id"],
            "required_fields": rf}
    return meta, builder, EP.EVENT_OPS, (lambda st, v, t: SO.event_prompt(st, g, v, t))


def psa_group(gen, gid, region, rng):
    country = region if region in ("UK", "IE", "US", "CA") else gen.eu_country(rng)
    key = country if country in ("UK", "IE", "US", "CA") else "EU"
    ok = lambda x: all("any" in FACT_REG.get(nb["fact_id"], ["any"]) or key in FACT_REG[nb["fact_id"]] for nb in x["numbers"])
    t = gen.pick("psa", PSAS, lambda x: region in x["regions"] and ok(x), rng)
    cur = LG.COUNTRIES[country]["currency"]
    car, cdesc, ars, realism = rng.choice(SO.PSA_CARRIERS)
    g = {"carrier": car, "carrier_desc": cdesc, "ar": rng.choice(ars), "realism": realism, "style": rng.choice(t["visual_styles"] + V.STYLES["psa"][:2]),
         "palette": palette("psa", rng)}
    g["artifacts"] = artifacts(realism, rng, car)

    def builder():
        return EP.build_psa(t, gid, country, C.rng_for("psa", gid), cur, country in ("US", "CA"), gen.fact_src), {}
    sp0, _ = builder()
    rf = ["Organiser", "Partner", "Title", "Knowledge sections", "Key warning", "Call to action", "Helpline", "Emergency number", "Reference code"]
    if sp0["source"]:
        rf.append("Source")
    if sp0["event"]:
        rf += ["Event date", "Event venue", "Places"]
    meta = {"sub_category": t["sub_category"], "country": country, "region": LG.COUNTRIES[country]["region"],
            "scene_type": cdesc.format(city=sp0["city"]["city"]), "product_type": "",
            "visual_style": "%s/%s" % (g["style"], g["palette"]), "layout": "psa_" + car, "aspect_ratio": g["ar"], "carrier": car,
            "realism": realism, "brand_or_organizer": sp0["organizer"], "product_or_title": sp0["title"], "source_archetype": t["id"],
            "required_fields": rf}
    return meta, builder, EP.PSA_OPS, (lambda st, v, tt: SO.psa_prompt(st, g, v, tt))


BUILD = {"Food label": label_group, "Commercial ad": ad_group, "Supplement": supp_group, "Event": event_group,
         "Public-service poster": psa_group}
COLS = ["id", "group_id", "variant", "lang", "super_category", "sub_category", "country", "region", "scene_type", "product_type",
        "visual_style", "layout", "aspect_ratio", "text_density", "required_fields", "tamper_types", "tampered_fields", "tamper_details",
        "difficulty", "single_image_detectable", "carrier", "realism", "brand_or_organizer", "product_or_title", "source_archetype", "prompt"]


def schedule():
    rng = C.rng_for("alloc")
    slots = []
    for cat in CATS:
        regs = [r for r, n in MARKETS[cat].items() for _ in range(n)]
        assert len(regs) == ALLOC[cat], cat
        rng.shuffle(regs)
        n = len(regs)
        slots += [((k + 0.5) / n, CATS.index(cat), cat, r) for k, r in enumerate(regs)]
    slots.sort()
    return [(c, r) for _, _, c, r in slots]


def run(n_groups, outdir):
    gen = Gen()
    sched = schedule()[:n_groups]
    for gi, (cat, reg) in enumerate(sched):
        gid = "G%04d" % (1001 + gi)
        rng = C.rng_for("group", gid)
        meta, builder, ops, render = BUILD[cat](gen, gid, reg, rng)
        gen.emit(gid, cat, meta, gen.variants(builder, ops, gid, cat, render), None)
    for k, r in enumerate(gen.rows):
        r["id"] = "P%06d" % (3001 + k)
    rows = [{c: r.get(c) for c in COLS} for r in gen.rows]
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, "poster_prompts_en_%d" % len(rows))
    with open(base + ".jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(base + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in rows:
            w.writerow([json.dumps(r[c], ensure_ascii=False) if isinstance(r[c], list) else ("" if r[c] is None else r[c]) for c in COLS])
    print("wrote", base, len(rows), "rows")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", type=int, default=334)
    ap.add_argument("--out", default=os.path.join("en", "final"))
    a = ap.parse_args()
    run(a.groups, a.out)
