"""Validate English content libraries.  Usage (repo root):  python en/src/validate_libs.py [module ...]
Prints 'OK <module> (<n> entries)' or a list of errors. Exit code 1 on any error."""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules_en as R

CLAIMS432 = {c["claim"] for c in json.load(open(os.path.join(HERE, "..", "refs", "eu432_claims.json"), encoding="utf-8"))}
FOOD_SUBS = ["Dairy & alternatives", "Beverages", "Breakfast cereals", "Snacks", "Confectionery", "Bakery & biscuits",
             "Spreads & sauces", "Ready meals & frozen", "Meat, fish & deli", "Canned & jarred", "Pasta, rice & grains",
             "Baby & kids", "Meal replacement & sports", "Seasonal"]
PACKS = {"box", "bag", "bottle", "can", "carton", "jar", "pot", "tub", "tray", "pouch", "wrapper", "multipack", "tin"}
MARKETS = {"UK", "IE", "MT", "US"}
EUROPE_NA = set("UK IE MT US CA DE FR NL BE LU ES PT IT AT CH DK SE NO FI IS PL CZ SK HU SI HR RO BG GR CY EE LV LT".split())
CAPS_OK = {"UHT", "MCT", "DHA", "EPA", "ALA", "GMO", "PDO", "PGI", "UK", "EU", "USA", "US", "BBQ", "XL", "NFC"}
SUPP_SUBS = ["Vitamins & minerals", "Bone & joint", "Omega-3 & fish oil", "Probiotics & gut", "Protein & sports",
             "Collagen & beauty", "Eye health", "Fibre", "Coenzyme Q10", "Botanicals", "Sleep & relaxation",
             "50+ multivitamin", "Kids", "Women's health", "Immune support", "Prenatal"]
REGION_GROUPS = {"US", "CA", "UK", "IE", "EU"}
SEASONS = set("any autumn winter spring halloween ca_thanksgiving us_thanksgiving black_friday st_martin sinterklaas "
              "christmas_market christmas new_year veganuary burns_night valentines carnival pancake_day mothers_day_uk "
              "st_patricks easter".split())
FACT_IDS = set(re.findall(r"^\| ([a-z0-9_]+) \|", open(os.path.join(HERE, "..", "refs", "facts_whitelist.md"),
                                                         encoding="utf-8").read(), flags=re.M)) - {"fact_id"}


def caps_words(s):
    return [w for w in re.findall(r"\b[A-Z][A-Z'\-]{2,}\b", s) if w not in CAPS_OK and not re.search(r"\d", w)]


def blacklist():
    try:
        return [b.lower() for b in importlib.import_module("lib_names_en").REAL_BRAND_BLACKLIST]
    except Exception:
        return []


def brand_hits(text, bl):
    t = text.lower()
    return [b for b in bl if re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", t)]


def all_strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from all_strings(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from all_strings(v)


def check_food(a, E):
    p = a.get("id", "?") + ": "
    for k in ["id", "sub_category", "legal_name", "names", "form", "origin_ok", "packages", "recipes", "eu_extra",
              "serving", "claims_ok", "health_claim", "selling", "exag_subtle", "exag_strong", "shelf", "shelf_tamper",
              "date_type", "storage", "storage_tamper", "prep", "animal_origin", "attr_tamper", "population",
              "may_contain", "visual"]:
        if k not in a:
            E.append(p + "missing " + k)
    if E and E[-1].startswith(p + "missing"):
        return
    if a["sub_category"] not in FOOD_SUBS: E.append(p + "bad sub_category")
    if a["form"] not in ("solid", "liquid"): E.append(p + "bad form")
    if not set(a["origin_ok"]) <= EUROPE_NA: E.append(p + "origin_ok outside Europe/NA")
    if not set(a.get("markets", MARKETS)) <= MARKETS: E.append(p + "bad markets")
    if not (2 <= len(a["packages"]) <= 5): E.append(p + "need 2-5 packages")
    for pk in a["packages"]:
        if pk.get("pack") not in PACKS: E.append(p + "bad pack " + str(pk.get("pack")))
        if pk.get("unit") not in ("g", "ml") or not isinstance(pk.get("net"), (int, float)): E.append(p + "bad net/unit")
        if (pk.get("unit") == "ml") != (a["form"] == "liquid"): E.append(p + "unit/form mismatch")
        pr = pk.get("price_eur")
        if not (isinstance(pr, list) and len(pr) == 2 and 0 < pr[0] < pr[1]): E.append(p + "bad price_eur")
    if not (1 <= len(a["recipes"]) <= 3): E.append(p + "need 1-3 recipes")
    for ri, r in enumerate(a["recipes"]):
        q = p + "recipe%d: " % ri
        ings = r["ing"]
        ps = [i["p"] for i in ings]
        if ps != sorted(ps, reverse=True): E.append(q + "ingredients not descending")
        if not (90 <= sum(ps) <= 110): E.append(q + "p sum %.1f" % sum(ps))
        heroes = [i for i in ings if i.get("hero")]
        n = r["nut"]
        for k in ["fat", "sat", "trans", "carb", "sugar", "added_sugar", "fibre", "protein", "salt", "cholesterol",
                  "calcium", "iron", "potassium", "vitd"]:
            if not isinstance(n.get(k), (int, float)): E.append(q + "nut missing " + k)
        if any(not isinstance(n.get(k), (int, float)) for k in ["fat", "sat", "carb", "sugar", "protein", "salt"]):
            continue
        if n["sugar"] > n["carb"] + 1e-9: E.append(q + "sugar>carb")
        if n.get("added_sugar", 0) > n["sugar"] + 1e-9: E.append(q + "added>sugar")
        if n["sat"] + n.get("trans", 0) > n["fat"] + 1e-9: E.append(q + "sat+trans>fat")
        if a["form"] == "solid" and n["fat"] + n["carb"] + n["protein"] + n.get("fibre", 0) > 100: E.append(q + "macros>100")
        sweet = any(any(w in i["n"].lower() for w in R.SUGAR_WORDS) for i in ings)
        if not sweet and n.get("added_sugar", 0) > 0: E.append(q + "added_sugar>0 but no sugar ingredient")
        if (sweet or n["fat"] > 10) and not heroes and ings[0]["p"] < 99: E.append(q + "needs a hero ingredient")
        for h in heroes:
            if h["p"] >= ings[0]["p"]: E.append(q + "hero p must be < first ingredient")
        for i in ings:
            tags = i.get("a", [])
            for t in tags:
                if not R.valid_tag(t): E.append(q + "bad allergen tag " + t)
            cw = caps_words(i["n"])
            if tags and not cw: E.append(q + "tagged but no CAPS allergen word: " + i["n"])
            if cw and not tags: E.append(q + "CAPS word but untagged: " + i["n"])
        _, kcal = R.energy(n)
        for c in a["claims_ok"]:
            if c not in R.EU_CLAIMS: E.append(q + "unknown claim " + c); continue
            if c == "No added sugars" and sweet: E.append(q + "No added sugars but sugar ingredient")
            elif not R.EU_CLAIMS[c](n, a["form"], kcal): E.append(q + "claim fails thresholds: " + c)
        for nm in r.get("names", []):
            if nm >= len(a["names"]): E.append(q + "names index out of range")
    for t in a["may_contain"]:
        if not R.valid_tag(t): E.append(p + "bad may_contain " + t)
    if a["health_claim"] and a["health_claim"] not in CLAIMS432: E.append(p + "health_claim not verbatim in eu432")
    for k, m in (("selling", 4), ("exag_subtle", 2), ("exag_strong", 3)):
        if len(a[k]) < m: E.append(p + "need >=%d %s" % (m, k))
    if a["date_type"] not in ("use_by", "best_before"): E.append(p + "bad date_type")
    for k in ("shelf", "shelf_tamper"):
        v = a[k]
        if not (isinstance(v, list) and v[1] in ("days", "months")): E.append(p + "bad " + k)
    if a["shelf"][1] == a["shelf_tamper"][1] and a["shelf_tamper"][0] <= a["shelf"][0]: E.append(p + "shelf_tamper not longer")
    if set(a["eu_extra"]) - {"fibre", "calcium", "iron", "vitd", "vitc", "potassium"}: E.append(p + "bad eu_extra")
    s = a["serving"]
    if not (isinstance(s, dict) and s.get("g") and s.get("us_household") and s.get("eu_label")): E.append(p + "bad serving")


def check_supp(s, E):
    p = s.get("id", "?") + ": "
    req = ["id", "sub_category", "regimes", "names", "form", "pack", "counts", "count_is_net", "price_eur", "dose",
           "actives", "ingredients", "hero_ing", "eu_claims", "us_claims", "upgrade", "selling", "exag_subtle",
           "exag_strong", "unsub", "attr_tamper", "suitable", "not_suitable", "pop_tamper", "extra_warnings", "shelf",
           "shelf_tamper", "storage", "allergens", "visual"]
    miss = [k for k in req if k not in s]
    if miss:
        E.append(p + "missing " + ",".join(miss)); return
    if s["sub_category"] not in SUPP_SUBS: E.append(p + "bad sub_category")
    if not set(s["regimes"]) <= {"US", "EU"} or not s["regimes"]: E.append(p + "bad regimes")
    if s["hero_ing"] not in [i["n"] for i in s["ingredients"]]: E.append(p + "hero_ing not in ingredients")
    mg = [i["mg"] for i in s["ingredients"]]
    if mg != sorted(mg, reverse=True): E.append(p + "ingredients not descending by mg")
    if s["hero_ing"] == s["ingredients"][0]["n"]: E.append(p + "hero_ing already first")
    for a in s["actives"]:
        nk = a.get("nrv_key")
        if nk is not None:
            if nk not in R.EU_NRV: E.append(p + "bad nrv_key " + nk)
            elif a.get("unit") != R.NUT_UNIT[nk]: E.append(p + "unit mismatch for " + nk)
        for nm in a.get("names", []):
            if nm >= len(s["names"]): E.append(p + "active names index out of range")
    for c in s["eu_claims"]:
        if c not in CLAIMS432: E.append(p + "eu_claim not verbatim: " + c[:50]); continue
        nut = c.split(" ")[0].lower()
        key = {"vitamin": None, "calcium": "calcium", "iron": "iron", "zinc": "zinc", "magnesium": "magnesium",
               "selenium": "selenium", "iodine": "iodine", "folate": "folate", "biotin": "biotin", "copper": "copper"}.get(nut)
        if nut == "vitamin":
            w = c.split(" ")[1].lower()
            key = {"a": "vita", "d": "vitd", "c": "vitc", "e": "vite", "k": "vitk", "b6": "vitb6", "b12": "vitb12"}.get(w)
        if key:
            amts = [a["amt"] for a in s["actives"] if a.get("nrv_key") == key]
            if not amts or min(amts) < 0.15 * R.EU_NRV[key]: E.append(p + "claim nutrient <15%% NRV: " + c[:40])
    for k, m in (("selling", 4), ("exag_subtle", 2), ("exag_strong", 3), ("unsub", 2), ("upgrade", 1)):
        if len(s[k]) < m: E.append(p + "need >=%d %s" % (m, k))
    for t in s["allergens"]:
        if not R.valid_tag(t): E.append(p + "bad allergen " + t)
    bad = re.compile(r"\b(cure|cures|treat|treats|prevent|prevents|disease|heal|heals)\b", re.I)
    for k in ("selling", "us_claims", "eu_claims"):
        for x in s[k]:
            if bad.search(x): E.append(p + "disease word in " + k + ": " + x)
    if s["shelf"][1] == s["shelf_tamper"][1] and s["shelf_tamper"][0] <= s["shelf"][0]: E.append(p + "shelf_tamper not longer")


def check_event(e, E):
    p = e.get("id", "?") + ": "
    req = ["id", "sub_category", "commercial", "regions", "season", "title_patterns", "subtitle", "product_hint", "agenda",
           "perks", "rules", "hidden_condition", "quota", "fee_eur", "venue_types", "duration_days", "daily_hours",
           "speaker_roles", "health_related", "disclaimer", "exag_line", "registration", "visual_styles", "visual_motif"]
    miss = [k for k in req if k not in e]
    if miss:
        E.append(p + "missing " + ",".join(miss)); return
    if not set(e["regions"]) <= REGION_GROUPS or not e["regions"]: E.append(p + "bad regions")
    if e["season"] not in SEASONS: E.append(p + "bad season")
    for t in e["title_patterns"]:
        if set(re.findall(r"\{(\w+)", t)) - {"brand", "city"}: E.append(p + "bad placeholder in title")
    if not (3 <= len(e["agenda"]) <= 6): E.append(p + "agenda 3-6 slots")
    prev = "00:00"
    for sl in e["agenda"]:
        if len(sl) != 3 or not all(re.fullmatch(r"\d\d:\d\d", x) for x in sl[:2]): E.append(p + "bad slot " + str(sl)); continue
        if not (prev <= sl[0] < sl[1]): E.append(p + "slots overlap/unordered " + str(sl))
        prev = sl[1]
    if not isinstance(e["quota"], int) or e["quota"] <= 0: E.append(p + "bad quota")
    if e["health_related"] and not e["disclaimer"]: E.append(p + "health event needs disclaimer")
    for k in ("perks", "rules"):
        if not (2 <= len(e[k]) <= 4): E.append(p + k + " 2-4")
    for x in all_strings(e):
        for m in re.findall(r"\{([^}]*)\}", x):
            if m not in ("brand", "city") and not re.fullmatch(r"money:\d+(\.\d+)?", m): E.append(p + "bad placeholder {" + m + "}")


def check_psa(t, E):
    p = t.get("id", "?") + ": "
    req = ["id", "sub_category", "regions", "season", "titles", "subtitles", "organizer_types", "sections", "numbers",
           "key_warning", "misinfo_subtle", "misinfo_strong", "cta", "has_event", "event_kinds", "visual_styles", "visual_motif"]
    miss = [k for k in req if k not in t]
    if miss:
        E.append(p + "missing " + ",".join(miss)); return
    if not set(t["regions"]) <= REGION_GROUPS or not t["regions"]: E.append(p + "bad regions")
    if t["season"] not in SEASONS: E.append(p + "bad season")
    if not (3 <= len(t["sections"]) <= 5): E.append(p + "sections 3-5")
    texts = list(t["subtitles"])
    for s in t["sections"]:
        if not (3 <= len(s["items"]) <= 6): E.append(p + "items 3-6 in " + s["heading"])
        for it in s["items"]:
            if len(it) > 90: E.append(p + "item >90 chars: " + it[:40])
        texts += s["items"]
    for nb in t["numbers"]:
        if nb["text"] not in texts: E.append(p + "number text not verbatim in items/subtitles: " + nb["text"][:40])
        if nb.get("fact_id") not in FACT_IDS: E.append(p + "unknown fact_id " + str(nb.get("fact_id")))
        if nb["tampered"] == nb["text"]: E.append(p + "tampered == text")
    if t["has_event"] and not t["event_kinds"]: E.append(p + "event_kinds empty")


def check_geo(m, E):
    need = EUROPE_NA
    if set(m.COUNTRIES) != need: E.append("COUNTRIES missing/extra: %s" % sorted(need ^ set(m.COUNTRIES)))
    for c, d in m.COUNTRIES.items():
        for k in ("name", "region", "currency", "lang_context", "date_style", "phone_fmt", "postcode_fmt", "cities"):
            if k not in d: E.append(c + " missing " + k)
        if len(d.get("cities", [])) < 4: E.append(c + " needs >=4 cities")
        if len(m.STREETS.get(c, [])) < 15: E.append(c + " needs >=15 streets")
        if len(m.VENUES.get(c, [])) < 8: E.append(c + " needs >=8 venues")
        if d.get("lang_context") == "international" and len(m.EN_CONTEXT.get(c, [])) < 4: E.append(c + " needs >=4 EN_CONTEXT")


def check_names(m, E):
    bl = [b.lower() for b in m.REAL_BRAND_BLACKLIST]
    if len(bl) < 250: E.append("blacklist < 250")
    for k, n in (("FOOD_BRAND_HEADS", 120), ("FOOD_BRAND_TAILS", 30), ("HEALTH_BRAND_HEADS", 60),
                 ("HEALTH_BRAND_TAILS", 20), ("FIRST_NAMES", 60), ("LAST_NAMES", 60)):
        if len(getattr(m, k)) < n: E.append(k + " < %d" % n)
        for w in getattr(m, k):
            for b in bl:
                if len(b) >= 5 and (b in w.lower() or (len(w) >= 5 and w.lower() in b)): E.append("%s '%s' ~ real '%s'" % (k, w, b))
    for g, lst in m.RETAILERS.items():
        if len(lst) < 10: E.append("RETAILERS[%s] < 10" % g)
        for w in lst:
            if brand_hits(w, bl): E.append("retailer '%s' hits blacklist" % w)
    for k, lst in m.ORG_PATTERNS.items():
        if len(lst) < 5: E.append("ORG_PATTERNS[%s] < 5" % k)
        for w in lst:
            if re.search(r"\b(NHS|FDA|WHO|USDA|CDC|EFSA|FSA|Red Cross)\b", w): E.append("real org in pattern " + w)


KIND = {"lib_food_en_a": "food", "lib_food_en_b": "food", "lib_food_en_c": "food", "lib_supp_en": "supp",
        "lib_event_en": "event", "lib_psa_en": "psa", "lib_geo_en": "geo", "lib_names_en": "names"}
ATTR = {"food": "ARCHETYPES", "supp": "SUPPLEMENTS", "event": "EVENTS", "psa": "PSA"}
FN = {"food": check_food, "supp": check_supp, "event": check_event, "psa": check_psa}


def main(mods):
    bad = False
    bl = blacklist()
    for mod in mods:
        E = []
        try:
            m = importlib.import_module(mod)
        except Exception as ex:
            print("FAIL import", mod, ex); bad = True; continue
        kind = KIND[mod]
        if kind in FN:
            items = getattr(m, ATTR[kind])
            ids = [x.get("id") for x in items]
            if len(ids) != len(set(ids)): E.append("duplicate ids")
            for x in items:
                FN[kind](x, E)
                hits = sorted({h for s in all_strings(x) for h in brand_hits(s, bl)})
                if hits: E.append(x.get("id", "?") + ": real brand words " + ",".join(hits))
            n = len(items)
        else:
            (check_geo if kind == "geo" else check_names)(m, E)
            n = 1
        if E:
            bad = True
            print("ERRORS in %s (%d):" % (mod, len(E)))
            for e in E[:200]:
                print("  -", e)
        else:
            print("OK %s (%d entries)" % (mod, n))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    args = sys.argv[1:] or [m for m in KIND if os.path.exists(os.path.join(HERE, m + ".py"))]
    main(args)
