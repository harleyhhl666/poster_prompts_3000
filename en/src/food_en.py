"""Food spec builder + text renderers (EU/UK/MT and US label regimes)."""
import re

import common_en as C
import rules_en as R

FRIDGE = {"EU": "5°C or below", "US": "40°F or below"}
FREEZER = {"EU": "-18°C or colder", "US": "0°F or below"}
COUNTRY_NAME = {}  # filled by generator from lib_geo_en


def regime_of(market):
    return "US" if market == "US" else "EU"


PACK_SYN = {"can": ["can", "tin"], "tin": ["tin", "can"], "pot": ["pot", "tub"], "tub": ["tub", "pot"], "bag": ["bag", "pouch", "packet"],
            "pouch": ["pouch", "bag", "sachet"], "box": ["box", "carton"], "carton": ["carton", "box", "brick"], "bottle": ["bottle"],
            "jar": ["jar"], "tray": ["tray"], "wrapper": ["wrapper", "flow-wrap", "foil"], "multipack": ["multipack", "pack of"]}
UNIT_WORDS = r"\b(container|pack|bar|pot|tube|pie|croissant|bag|can|bottle|carton|tub|pouch|bun|pizza|tray|sachet|pieces?|slices?|biscuits?|cookies?|links?|sausages?|fillets?|fingers?)\b"


def pack_in_visual(pack, visual):
    v = visual.lower()
    return any(re.search(r"\b" + w, v) for w in PACK_SYN.get(pack, [pack]))


def serving_labels(arc, pk, serv, reg):
    """portion labels that cannot contradict the chosen pack: keep the library label only when it names a fraction/unit
    consistent with the pack, otherwise fall back to a plain weight/volume."""
    unit = "g" if arc["form"] == "solid" else "ml"
    eu, us = arc["serving"]["eu_label"], arc["serving"]["us_household"]
    unit_net = pk["net"]
    def consistent(lbl):
        if re.search(r"\b1/(\d)", lbl):
            k = int(re.search(r"\b1/(\d)", lbl).group(1))
            return abs(unit_net / k - serv) <= 0.06 * serv
        if re.search(UNIT_WORDS, lbl, re.I):
            m = re.match(r"\s*(\d+)\s", lbl)
            n = int(m.group(1)) if m else 1
            if re.search(r"\b(container|pack|pot|tube|bag|can|bottle|carton|tub|pouch|bar|pizza|tray|sachet)\b", lbl, re.I):
                return abs(unit_net * n - serv) <= 0.06 * serv
            return True  # pieces/slices/biscuits: count-based, no pack contradiction
        return True
    eu_l = eu if (consistent(eu) and re.search(r"\d", eu)) else "%d%s" % (serv, unit)
    if not re.search(r"\(\d+\s?(g|ml)\)|\d+\s?(g|ml)\b", eu_l):   # '75g (dry)' already states the weight
        eu_l = "%s (%d%s)" % (eu_l, serv, unit)
    if arc["form"] == "liquid":
        us_l = "8 fl oz" if serv == 240 else "%s fl oz" % C._n1(serv / 29.5735)
    else:
        us_l = us if consistent(us) else "%s oz" % C._n1(serv / 28.3495)
        us_l = re.sub(r"\s*\(\d+\s?g\)", "", us_l)
    return eu_l, us_l


COUNT_WORDS = r"\b(two|three|four|five|six|eight|ten|twelve|dozen)\b|\d+\s?(x|pack|pieces|pies|bars|pots)\b"


PLACES = [(r"ital|po valley|sicil|tuscan|parma|neapolitan|tricolou?r|green-white-red", "IT"), (r"\bgreek|greece|cretan", "GR"),
          (r"norw", "NO"), (r"scot|british|welsh|\benglish|cornish|yorkshire", "UK"), (r"\birish|ireland", "IE"),
          (r"spanish|spain|iberian|andalu", "ES"), (r"french|france|breton|provenc", "FR"), (r"german|bavarian|black forest", "DE"),
          (r"\bdutch|holland|gouda", "NL"), (r"belgian|belgium", "BE"), (r"danish|denmark", "DK"), (r"swedish|sweden", "SE"),
          (r"polish|poland", "PL"), (r"\bswiss|switzerland", "CH"), (r"portug", "PT"), (r"icelandic|iceland", "IS"),
          (r"finnish|finland", "FI"), (r"canadian|canada|quebec", "CA"), (r"\bamerican|\busa\b|vermont|california", "US"),
          (r"austrian|austria", "AT")]


def pack_copy_ok(x, pk):
    t = x.lower()
    if re.search(r"squeez", t) and pk["pack"] not in ("bottle", "pouch", "tube"):
        return False
    if re.search(r"individually wrapped|each one wrapped", t) and pk["count"] < 2:
        return False
    if re.search(r"ring-pull|easy-open can|in a can\b", t) and pk["pack"] not in ("can", "tin"):
        return False
    if re.search(r"resealable", t) and pk["pack"] in ("can", "tin", "carton", "box", "wrapper"):
        return False
    return True


HARVEST = r"harvest|freshly picked|picked at|within hours of picking|new season"


def season_ok(x, prod):
    """harvest-freshness copy only when the production date is in the Northern-hemisphere harvest window"""
    return not re.search(HARVEST, x, re.I) or 6 <= prod.month <= 10


def place_of(text):
    t = text.lower()
    hits = {cc for pat, cc in PLACES if re.search(pat, t)}
    return hits.pop() if len(hits) == 1 else None


def place_ok(x, origin):
    p = place_of(x)
    return p is None or p == origin


FLAVOURS = ["banana", "strawberr", "raspberr", "blueberr", "mango", "apricot", "apple", "pear", "cinnamon", "ginger", "coconut",
            "dill", "garlic", "chilli", "paprika", "basil", "spinach", "mushroom", "peanut", "almond", "hazelnut", "vanilla", "cranberr",
            "pistachio", "walnut", "sesame", "rosemary", "truffle", "caramel"]


FLAVOUR_ALIAS = {"citrus": r"\b(citrus|lemon|lime|orange|grapefruit|mandarin|clementine|yuzu)", "chocolate": r"\b(chocolate|cocoa|cacao)",
                 "cocoa": r"\b(chocolate|cocoa|cacao)", "berry": r"berr|blackcurrant|redcurrant", "lemon": r"\blemon", "lime": r"\blime",
                 "orange": r"\borange", "mint": r"\b(mint|peppermint|spearmint)", "honey": r"\bhoney", "maple": r"\bmaple",
                 "coffee": r"\b(coffee|espresso)", "cherry": r"\bcherr", "peach": r"\bpeach", "tropical": r"mango|pineapple|passion|papaya|guava"}


def flavour_ok(x, ingtext):
    t, xl = ingtext.lower(), x.lower()
    if not all(re.search(r"\b" + w[:5], t) for w in FLAVOURS if re.search(r"\b" + w, xl)):
        return False
    # flavour words in copy must be backed by an ingredient (review: 'citrus taste' on a mixed-berry drink)
    return all(re.search(pat, t) for w, pat in FLAVOUR_ALIAS.items() if re.search(r"\b" + w + r"(y|ies|s)?\b", xl))


def visual_clean(v, ingtext):
    """drop pack-look clauses that describe another recipe variant (flavour not in this recipe, 'X or Y', '... variant',
    printed badges with numbers that are not quoted)"""
    out = []
    for k, c in enumerate(re.split(r",\s*|;\s*", v)):
        if re.search(r"\bvariant\b|\d+\s?g\b|['\"]", c, re.I):
            continue
        if re.search(r"\bor\b", c):
            if k == 0:
                c = re.sub(r"\s+or\s+[\w-]+", "", c)
            else:
                continue
        if not flavour_ok(c, ingtext):
            if k == 0:
                for w in FLAVOURS:
                    if re.search(r"\b" + w, c, re.I) and not re.search(r"\b" + w[:5], ingtext.lower()):
                        c = re.sub(r"\s*(?:and|&)\s+" + w + r"\w*|\b" + w + r"\w*\s+(?:and|&)\s+|\b" + w + r"\w*\s*", " ", c, flags=re.I)
                c = re.sub(r"\s{2,}", " ", c).strip()
            else:
                continue
        out.append(c)
    return ", ".join(out) if out else v.split(",")[0]


FREE_SYN = {"sugar": R.SUGAR_WORDS, "dairy": ["milk", "cream", "butter", "whey", "cheese", "yog", "lactose"],
            "gluten": ["wheat", "barley", "rye", "oat", "spelt"], "nut": ["almond", "hazelnut", "walnut", "cashew", "pecan", "pistachio", "macadamia"],
            "palm": ["palm"], "egg": ["egg"], "soy": ["soy"], "soya": ["soy"]}


def copy_ok(x, sp=None, ingtext=None, amounts=True):
    """drop selling lines that can contradict the generated spec: nutrient amounts (jittered), pack counts,
    'no X' / 'X-free' when X is an ingredient"""
    if amounts and (re.search(r"\d+(\.\d+)?\s?(g|mg|kcal|calories|kj)\b", x, re.I) or re.search(COUNT_WORDS, x, re.I)):
        return False
    ings = ingtext if ingtext is not None else " ".join((i["eu"] + " " + (i.get("us") or "")).lower() for i in sp["ings"])
    ings = ings.lower()
    for m in re.finditer(r"\b(?:no|zero|without|free from)\s+(?:added\s+)?([a-z]+)|\b([a-z]+)[- ]free\b", x.lower()):
        w = m.group(1) or m.group(2) or ""
        syn = FREE_SYN.get(w.rstrip("s"), [w[:5]] if len(w) > 2 else [])
        if w not in ("artificial", "nasties", "compromise") and any(re.search(r"\b" + re.escape(s), ings) for s in syn):
            return False
    return True


def jitter(n, rng, f=0.05):
    out = {}
    for k, v in n.items():
        if isinstance(v, (int, float)) and v > 0:
            out[k] = v * (1 + rng.uniform(-f, f))
        else:
            out[k] = v
    out["sugar"] = min(out["sugar"], out["carb"])
    out["added_sugar"] = min(out.get("added_sugar", 0), out["sugar"])
    out["sat"] = min(out["sat"], out["fat"] - out.get("trans", 0))
    return out


def us_claims(spec):
    """map EU claim keys to US nutrient-content claims checked per serving (RACC approximated by serving size)."""
    s = spec["us_serv"]
    out = []
    for c in spec["claims_eu"]:
        if c == "Low fat" and s["fat"] <= 3: out.append("Low fat")
        elif c == "Fat free" and s["fat"] < 0.5: out.append("Fat free")
        elif c == "Sugars free" and s["sugar"] < 0.5: out.append("Sugar free")
        elif c == "Low salt" and s["sodium"] <= 140: out.append("Low sodium")
        elif c in ("Source of fibre", "High fibre"):
            p = s["fibre"] / R.US_DV["fibre"] * 100
            if p >= 20: out.append("Excellent source of fiber")
            elif p >= 10: out.append("Good source of fiber")
        elif c.startswith("Source of ") or c == "High in calcium":
            key = {"calcium": "calcium", "vitamin D": "vitd", "iron": "iron", "vitamin C": "vitc"}.get(c.replace("Source of ", "").replace("High in ", ""))
            if key and key in s:
                p = s[key] / R.US_DV[key] * 100
                nm = {"vitd": "vitamin D", "vitc": "vitamin C"}.get(key, key)
                if p >= 20: out.append("Excellent source of " + nm)
                elif p >= 10: out.append("Good source of " + nm)
    return list(dict.fromkeys(out))


def lower_caps(s):
    return re.sub(r"\b([A-Z][A-Z'\-]{2,})\b", lambda m: m.group(1).lower() if m.group(1) not in ("UHT", "MCT", "DHA", "EPA", "PDO", "PGI") else m.group(1), s)


def ing_eu(i):
    t = i["eu"] if i["emph"] else lower_caps(i["eu"])
    if i.get("quid") is not None:
        t += " (%s%%)" % i["quid"]
    return t


US_FUNC = r"^(?:humectant|stabili[sz]ers?|emulsifiers?|acidity regulators?|preservatives?|antioxidants?|thickeners?|raising agents?|colou?rs?|sweeteners?|gelling agents?|firming agents?|anti-caking agents?|glazing agents?|flavou?r enhancers?|acids?|bulking agents?)\s*:\s*"


def ing_us(i):
    t = re.sub(US_FUNC, "", (i.get("us") or i["eu"]), flags=re.I)   # EU function-class prefixes are not US style
    if i.get("quid") is not None:
        t += " (%s%%)" % i["quid"]
    return t.upper()


def quid_str(p):
    return ("%d" % round(p)) if p >= 2 else ("%.1f" % p).rstrip("0").rstrip(".")


def build(arc, gid, market, brand, ref, rng, geo, pack_filter=None):
    """returns spec dict (clean). geo: helper object with addr(country, rng), company(brand,country,rng)."""
    reg = regime_of(market)
    ni = rng.randrange(len(arc["names"]))
    recs = [r for r in arc["recipes"] if ni in r.get("names", range(len(arc["names"])))] or arc["recipes"]
    rec = rng.choice(recs)
    packs = [p for p in arc["packages"] if (pack_filter is None or pack_filter(p))] or arc["packages"]
    vis = [p for p in packs if pack_in_visual(p["pack"], arc["visual"])]
    pk = rng.choice(vis or packs)
    origins = arc["origin_ok"]
    home = market if market in origins else None
    implied = place_of(arc["names"][ni] + " " + arc["legal_name"] + " " + arc["visual"])
    if implied and implied in origins:
        origins = [implied]
        home = implied if implied == market else None
    NA = {"US", "CA"}
    if arc["date_type"] == "use_by" or (arc["shelf"][1] == "days" and arc["shelf"][0] <= 30):
        # short-life chilled food: made in the market itself or at least on the same continent
        same = [o for o in origins if (o in NA) == (market in NA)]
        origins = ([home] if home and rng.random() < 0.7 else []) or same or origins
    origin = home if (home and rng.random() < 0.5) else rng.choice(origins)
    sp = {"gid": gid, "arc": arc, "market": market, "regime": reg, "brand": brand,
          "name": "%s %s" % (brand, arc["names"][ni]), "core": arc["names"][ni], "legal": arc["legal_name"],
          "form": arc["form"], "pack": pk, "origin": origin, "sub": arc["sub_category"]}
    # ingredients
    ings = []
    for x in rec["ing"]:
        is_fat = re.search(r"\b(oil|butter|fat|lard)\b", x["n"], re.I) and not x.get("quid")
        q = quid_str(x["p"]) if (x.get("quid") or (x.get("hero") and not is_fat)) and x["p"] < 99 and reg == "EU" else None
        ings.append({"eu": x["n"], "us": x.get("us"), "p": x["p"], "a": list(x.get("a", [])), "hero": bool(x.get("hero")),
                     "quid": q, "emph": True})
    sp["ings"] = ings
    sp["may"] = list(arc["may_contain"])
    sp["contains_drop"] = set()   # US 'Contains' words removed by tamper
    sp["contains_extra_note"] = None
    # nutrition
    n = jitter(rec["nut"], rng)
    sp["n100"] = n
    kj, kcal = R.energy(n)
    sp["kj"], sp["kcal"] = kj, kcal
    claims = [c for c in arc["claims_ok"] if R.EU_CLAIMS[c](n, arc["form"], kcal)]
    sp["claims_eu"] = claims
    serv = arc["serving"]["g"]
    unit_w = "g" if arc["form"] == "solid" else "ml"
    if reg == "US" and arc["form"] == "liquid" and re.search(r"beverage|drink|juice|milk|kefir|smoothie|lemonade|tea|coffee|water|soda|cola",
                                                             arc["sub_category"] + " " + arc["legal_name"], re.I) \
            and not re.search(r"squash|cordial|concentrate|syrup|shot|cream|sauce|oil|vinegar", arc["legal_name"], re.I):
        serv = 240   # FDA RACC for beverages: 8 fl oz (21 CFR 101.12(b) Table 2)
    if pk["count"] > 1 and 0.5 * serv <= pk["net"] <= 2 * serv and abs(pk["net"] - serv) > 0.1 * serv:
        serv = pk["net"]   # multipack of pieces: the portion is one piece (review: '6 x 60g' vs 'Per 1 croissant (45g)')
    elif reg != "US" and pk["count"] == 1 and pk["net"] / serv < 2:
        serv = pk["net"]   # portion larger than half the pack: declare the whole pack (review: 100g panettone, 75g slice)
    sp["serv_eu"], sp["serv_us"] = serving_labels(arc, pk, serv, reg)
    if serv != arc["serving"]["g"] and reg != "US":
        if not re.match(r"\s*1 (?!slice|portion|serving|bowl|glass|cup|tbsp|tsp|handful|scoop)\w+", sp["serv_eu"]) or pk["count"] == 1:
            pw = {"multipack": "piece", "wrapper": "bar" if "bar" in arc["legal_name"].lower() else "pack", "tray": "pack"}.get(pk["pack"], pk["pack"])
            sp["serv_eu"] = "1 %s (%d%s)" % (pw, serv, unit_w)
        else:
            sp["serv_eu"] = re.sub(r"\(\d+\s?(g|ml)\)", "(%d%s)" % (serv, unit_w), sp["serv_eu"])
    if reg == "US" and pk["count"] == 1 and pk["net"] / serv < 2:
        # single-serving container: declare the whole unit as one serving (21 CFR 101.9(b)(6))
        serv = pk["net"]
        sp["serv_us"] = "1 %s" % ({"multipack": "pack", "wrapper": "bar" if "bar" in arc["legal_name"].lower() else "pack"}.get(pk["pack"], pk["pack"]))
    if reg == "US" and pk["count"] > 1 and abs(pk["net"] - serv) <= 0.1 * serv and not re.search(UNIT_WORDS, sp["serv_us"], re.I):
        sp["serv_us"] = "1 piece"
    sp["serv_g"] = serv
    f = serv / 100.0
    us = {k: (v * f if isinstance(v, (int, float)) else v) for k, v in n.items()}
    us["sodium"] = n["salt"] / 2.5 * 1000 * f
    us["kcal"] = kcal * f
    sp["us_serv"] = us
    if "Fat free" in claims and "Low fat" in claims:
        claims.remove("Low fat")
    if "Sugars free" in claims and "Low sugars" in claims:
        claims.remove("Low sugars")
    sp["claims_eu"] = claims
    # US: keep only 'good/excellent source' claims (low/free claims on naturally low foods need FDA qualifiers;
    # vitamin C is not a mandatory Nutrition Facts row)
    sp["claims"] = claims if reg == "EU" else [c for c in us_claims(sp) if "source" in c and "vitamin C" not in c]
    sp["health_claim"] = arc["health_claim"] if (reg == "EU" and arc["health_claim"] and claims) else None
    sp["eu_extra"] = [k for k in arc["eu_extra"] if k in n]
    sp["table"] = eu_table(sp) if reg == "EU" else us_table(sp)
    sp["table_note"] = None
    # pack / quantity
    unit = "g" if arc["form"] == "solid" else "ml"
    net, cnt = pk["net"], pk["count"]
    if reg == "EU":
        sp["net_front"] = (C.eu_net(net, unit) + " ℮") if cnt == 1 else "%d x %s" % (cnt, C.eu_net(net, unit))
    else:
        sp["net_front"] = C.us_net(net * cnt, unit) if cnt == 1 else "%d x %s" % (cnt, C.us_net(net, unit).replace("NET WT ", ""))
    sp["net_back"] = sp["net_front"]
    total = net * cnt
    sp["servings"] = total / serv
    # dates
    sv, su = arc["shelf"]
    sp["shelf"] = [sv, su]
    span = sv * 30 if su == "months" else sv
    back = rng.randint(2, max(3, min(90, int(span * 0.35))))
    prod = C.add_days(ref, -back)
    sp["prod"] = prod
    sp["exp"] = C.expiry_of(prod, sv, su)
    sp["date_kind"] = "Use by" if arc["date_type"] == "use_by" else "Best before"
    sp["date_style"] = rng.choice(C.DATE_STYLES["us" if reg == "US" else "eu"])
    sp["lot_style"] = "LOT YYMMDD-NN" if reg == "US" else rng.choice(C.LOT_STYLES)
    sp["lot_line"] = rng.choice("ABCDEFGHKM")
    sp["lot_nn"] = "%02d" % rng.randint(1, 24)
    sp["lot"] = C.lot_code(prod, sp["lot_style"], sp["lot_line"], sp["lot_nn"])
    sp["ink_lot"] = sp["lot"]
    sp["ink_exp"] = sp["exp"]
    sp["ink_place"] = {"bottle": "the shoulder of the bottle", "can": "the base of the can", "tin": "the base of the tin",
                       "jar": "the lid", "pot": "the foil lid", "tub": "the side of the tub",
                       "carton": "the top seam of the carton", "box": "the top flap", "bag": "the top seal of the bag",
                       "tray": "the film lid", "pouch": "the top seal", "wrapper": "the back seam",
                       "multipack": "the outer wrap"}.get(pk["pack"], "the top of the pack")
    # storage etc
    fill = lambda s: s.replace("{fridge}", FRIDGE[reg]).replace("{freezer}", FREEZER[reg]) if s else s
    sp["storage"] = C.us_temps(fill(arc["storage"])) if reg == "US" else fill(arc["storage"])
    sp["storage_tamper"] = C.us_temps(fill(arc["storage_tamper"])) if reg == "US" else fill(arc["storage_tamper"])
    for k in ("storage", "storage_tamper"):
        if sp[k]:
            sp[k] = re.sub(r"(or (?:colder|below|lower))(?: or (?:colder|below|lower))+", r"\1", sp[k])
    sp["prep"] = C.us_temps(arc["prep"]) if (reg == "US" and arc["prep"]) else arc["prep"]
    sp["population"] = arc["population"]
    # producer / importer
    comp = geo.company(brand, origin, rng)
    sp["producer"] = comp
    sp["importer"] = None
    if origin != market and not (market in ("UK", "IE", "MT") and False):
        sp["importer"] = geo.company(brand, market, rng, importer=True)
    sp["origin_badge"] = ("Made in " if origin in ("US", "CA", "UK") else "Product of ") + C.the(geo.country_name(origin))
    sp["care_addr_same"] = True
    sp["barcode"] = C.upca(rng) if reg == "US" else C.ean13(rng, C.GS1.get(origin if origin in C.GS1 else market, "50"))
    # copy
    sp["visual"] = visual_clean(arc["visual"], " ".join(i["eu"] for i in sp["ings"]) + " " + sp["core"])
    sel = [x for x in arc["selling"] if copy_ok(x, sp) and place_ok(x, origin) and pack_copy_ok(x, pk) and season_ok(x, sp["prod"]) and flavour_ok(x, " ".join(i["eu"] for i in sp["ings"]) + " " + sp["core"])
           and not (reg == "US" and re.search(r"naturally contain sugars", x, re.I))] or [x for x in arc["selling"] if not re.search(r"\d", x)][:2]
    rng.shuffle(sel)
    sp["selling"] = sel[:rng.choice([3, 4])]
    sp["front_claims"] = []      # tamper-inserted claim texts (nutrition/efficacy/attribute/free-from)
    sp["headline_extra"] = None
    sp["attr"] = None
    sp["free_from"] = None
    sp["warning_removed"] = []
    sp["quid_front"] = None
    return sp


def eu_table(sp):
    n, f = sp["n100"], sp["serv_g"] / 100.0
    rows = []
    kj, kcal = sp["kj"], sp["kcal"]
    rows.append(["Energy", "%dkJ / %dkcal" % (round(kj), round(kcal)), "%dkJ / %dkcal" % (round(kj * f), round(kcal * f)),
                 C.pct(kj * f / R.EU_RI["energy_kj"] * 100)])
    spec_rows = [("Fat", "fat"), ("of which saturates", "sat"), ("Carbohydrate", "carb"), ("of which sugars", "sugar")]
    if "fibre" in sp["eu_extra"] or n.get("fibre", 0) >= 0.5:
        spec_rows.append(("Fibre", "fibre"))
    spec_rows += [("Protein", "protein"), ("Salt", "salt")]
    for lab, k in spec_rows:
        ri = C.pct(n[k] * f / R.EU_RI[k] * 100) if k in R.EU_RI else "-"
        rows.append([lab, C.g_eu(k, n[k]), C.g_eu(k, n[k] * f), ri])
    for k in sp["eu_extra"]:
        if k == "fibre":
            continue
        u = R.NUT_UNIT[k]
        v = n[k]
        vs = ("%.1f" % v if v < 10 else "%d" % round(v)) + u
        vss = ("%.1f" % (v * f) if v * f < 10 else "%d" % round(v * f)) + u
        rows.append([R.NUT_LABEL[k], vs + " (%s NRV)" % C.pct(v / R.EU_NRV[k] * 100), vss, "-"])
    return {"kind": "EU", "rows": rows, "serv_label": sp["serv_eu"]}


def us_table(sp):
    s = sp["us_serv"]
    cal = C.r_us_cal(s["kcal"])
    rows = []
    def dv(k, v):   # %DV from the declared (rounded) amount, so a 0g row always shows 0%
        return C.pct(v / R.US_DV[k] * 100)
    tot_carb = s["carb"] + s.get("fibre", 0)
    rows.append(["Total Fat", C.fmt_g(C.r_us_fat(s["fat"])), dv("fat", C.r_us_fat(s["fat"]))])
    rows.append(["  Saturated Fat", C.fmt_g(C.r_us_fat(s["sat"])), dv("sat", C.r_us_fat(s["sat"]))])
    rows.append(["  Trans Fat", C.fmt_g(C.r_us_fat(s.get("trans", 0))), ""])
    rows.append(["Cholesterol", "%dmg" % C.r_us_chol(s.get("cholesterol", 0)), dv("cholesterol", C.r_us_chol(s.get("cholesterol", 0)))])
    rows.append(["Sodium", "%dmg" % C.r_us_sodium(s["sodium"]), dv("sodium", C.r_us_sodium(s["sodium"]))])
    rows.append(["Total Carbohydrate", "%dg" % C.r_us_g(tot_carb), dv("carb_total", C.r_us_g(tot_carb))])
    rows.append(["  Dietary Fiber", "%dg" % C.r_us_g(s.get("fibre", 0)), dv("fibre", C.r_us_g(s.get("fibre", 0)))])
    rows.append(["  Total Sugars", "%dg" % C.r_us_g(s["sugar"]), ""])
    rows.append(["    Includes %dg Added Sugars" % C.r_us_g(s.get("added_sugar", 0)), "", dv("added_sugar", C.r_us_g(s.get("added_sugar", 0)))])
    rows.append(["Protein", "%dg" % C.r_us_g(s["protein"]), ""])
    vd = s.get("vitd", 0); ca = s.get("calcium", 0); fe = s.get("iron", 0); k = s.get("potassium", 0)
    vd_, ca_, fe_, k_ = round(vd * 10) / 10, 10 * round(ca / 10), round(fe * 10) / 10, 10 * round(k / 10)
    rows.append(["Vitamin D", ("%gmcg" % vd_) if vd_ else "0mcg", dv("vitd", vd_)])
    rows.append(["Calcium", "%dmg" % ca_, dv("calcium", ca_)])
    rows.append(["Iron", ("%gmg" % fe_) if fe_ else "0mg", dv("iron", fe_)])
    rows.append(["Potassium", "%dmg" % k_, dv("potassium", k_)])
    sv = sp["servings"] if "servings" in sp else None
    return {"kind": "US", "rows": rows, "calories": cal, "household": sp["serv_us"]}


def servings_text(x):
    if x < 2:
        return "1 serving per container"
    if x <= 5:
        v = round(x * 2) / 2
        return "about %s servings per container" % (("%g" % v))
    return "about %d servings per container" % round(x)


# ------------------------------------------------------------------ text pieces used by scenes
def d(sp, date):
    return C.fmt_date(date, sp["date_style"])


def ingredients_text(sp):
    if sp["regime"] == "EU":
        return "Ingredients: " + ", ".join(ing_eu(i) for i in sp["ings"]) + "."
    return "INGREDIENTS: " + ", ".join(ing_us(i) for i in sp["ings"]) + "."


def contains_words(sp, include_dropped=False):
    out = []
    if any("pine nut" in (i["eu"] + " " + (i.get("us") or "")).lower() for i in sp["ings"]):
        out.append("Pine Nuts")   # FDA 2025 guidance lists pine nut among tree nuts (not an EU Annex II nut)
    for i in sp["ings"]:
        for t in i["a"]:
            w = R.us_allergen_word(t)
            if w and w not in out:
                out.append(w)
    return out if include_dropped else [w for w in out if w not in sp["contains_drop"]]


def allergen_lines(sp):
    """list of lines (may be empty when deleted by tamper)."""
    L = []
    has = any(i["a"] for i in sp["ings"])
    if sp["regime"] == "EU":
        if has and not sp.get("allergy_advice_removed"):
            L.append(sp.get("allergy_advice") or "Allergy advice: for allergens, including cereals containing gluten, see ingredients in CAPITALS.")
        if sp["may"] and not sp.get("may_removed"):
            L.append("May contain " + " and ".join(may_word(t, "EU") for t in sp["may"]) + ".")
    else:
        w = contains_words(sp)
        if w:
            L.append("CONTAINS: " + ", ".join(x.upper() for x in w) + ".")
        if sp["may"] and not sp.get("may_removed"):
            mw = [may_word(t, "US") for t in sp["may"]]
            mw = [x for x in mw if x]
            if mw:
                L.append("MAY CONTAIN " + ", ".join(mw) + ".")
    return L


def may_word(tag, reg):
    g, _, s = tag.partition(":")
    if reg == "US":
        w = R.us_allergen_word(tag)
        if not w:
            return None
        if g == "nuts":
            return "TREE NUTS (%s)" % w.upper()
        return w.upper()
    if g == "nuts":
        return "NUTS (%s)" % {"brazil": "BRAZIL NUTS"}.get(s, (s + "s").upper() if not s.endswith("s") else s.upper())
    if g == "gluten":
        return s.upper() if s != "oats" else "OATS"
    return {"crustaceans": "CRUSTACEANS", "fish": "FISH", "molluscs": "MOLLUSCS", "soybeans": "SOYA",
            "sulphites": "SULPHITES", "eggs": "EGGS"}.get(g, g.upper())


def date_lines(sp):
    if sp["regime"] == "EU":
        return ["Production date: " + d(sp, sp["prod"]), "%s: %s" % (sp["date_kind"], d(sp, sp["exp"])),
                "Shelf life (unopened): " + C.shelf_str(*sp["shelf"]), sp["lot"] if sp["lot"].startswith("LOT") else "Lot: " + sp["lot"]]
    return ["PROD: " + d(sp, sp["prod"]), "%s: %s" % ("USE BY" if sp["date_kind"] == "Use by" else "BEST BY", d(sp, sp["exp"])),
            "Shelf life (unopened): " + C.shelf_str(*sp["shelf"]), sp["lot"] if sp["lot"].startswith("LOT") else "LOT " + sp["lot"]]


def inkjet_text(sp):
    k = ("BB" if sp["date_kind"] == "Best before" else "USE BY") if sp["regime"] == "EU" else ("BEST BY" if sp["date_kind"] == "Best before" else "USE BY")
    return "%s %s  %s" % (k, d(sp, sp["ink_exp"]), sp["ink_lot"])


def producer_lines(sp):
    p = sp["producer"]
    L = []
    if sp["importer"]:
        imp = sp["importer"]
        L.append("Produced in %s by %s, %s." % (C.the(p["country"]), p["name"], p["addr"]))
        if not sp.get("importer_removed"):
            L.append(("Imported by: " if sp["regime"] == "US" else "Imported and distributed by: ") + "%s, %s." % (imp["name"], imp["addr"]))
    else:
        L.append(("Manufactured by: " if sp["regime"] == "US" else "Produced by: ") + "%s, %s." % (p["name"], p["addr"]))
    return L


def care_line(sp):
    who = sp["importer"] or sp["producer"]
    addr = who.get("addr_care", who["addr"])
    return "Questions or comments? Write to %s, %s or call %s." % (who["name"], addr, who["phone"])


def storage_line(sp):
    return sp["storage"]
