"""QA for the English prompts (re-derives everything from prompt text, not engine state).
Usage: python en/src/qa_en.py en/final/poster_prompts_en_1002.jsonl"""
import datetime as dt
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_en as C
import rules_en as R

MON3 = {m: i + 1 for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
MONF = {m: i + 1 for i, m in enumerate(C.MON)}
WD = {w: i for i, w in enumerate(C.WEEKDAY)}
WD3 = {w: i for i, w in enumerate(C.WD3)}


def quoted(p):
    return re.findall("「(.*?)」", p, flags=re.S)


def body(p):
    i = p.find("This is the normal reference version")
    j = p.find("This is a research sample")
    k = min(x for x in (i, j, len(p)) if x >= 0)
    return p[:k]


def pdate(s, us):
    s = s.strip()
    m = re.fullmatch(r"(\d\d)[./](\d\d)[./](\d{2,4})", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        return dt.date(y, a, b) if us else dt.date(y, b, a)
    m = re.fullmatch(r"(\d\d) ([A-Z]{3}) (\d{4})", s)
    if m:
        return dt.date(int(m.group(3)), MON3[m.group(2)], int(m.group(1)))
    m = re.fullmatch(r"([A-Z]{3}) (\d\d) (\d{4})", s)
    if m:
        return dt.date(int(m.group(3)), MON3[m.group(1)], int(m.group(2)))
    return None


def check_dates(q, us):
    """returns (matched, list of violations)"""
    J = "\n".join(q)
    v = []
    pm = re.search(r"(?:Production date|PROD|Date of manufacture|MFG): ([^\n]+)", J)
    em = re.search(r"(?:Best before|Use by|BEST BY|USE BY|EXP): ([^\n]+)", J)
    sm = re.search(r"Shelf life(?: \(unopened\))?: (\d+) (day|days|month|months)\b", J)
    lm = re.search(r"(?:Lot|LOT):? (L ?\d[\dA-Z ]*|LOT \d+-\d+|\d{6}-\d+|L\d+[A-Z])", J)
    if not (pm and em and sm):
        return False, v
    prod, exp = pdate(pm.group(1), us), pdate(em.group(1), us)
    if not prod or not exp:
        return False, ["unparsed date"]
    unit = "months" if sm.group(2).startswith("month") else "days"
    if C.expiry_of(prod, int(sm.group(1)), unit) != exp:
        v.append("expiry != prod+shelf-1")
    lot = None
    for m in re.finditer(r"\b(L\d{5}[A-Z]|L \d{6} [A-Z]|LOT \d{6}-\d\d|L\d{8}[A-Z])\b", J):
        lot = m.group(1)
        break
    if lot:
        st = "L YYDDD+A" if re.fullmatch(r"L\d{5}[A-Z]", lot) else "L DDMMYY A" if lot.startswith("L ") else "LOT YYMMDD-NN" if lot.startswith("LOT") else "L YYYYMMDD A"
        try:
            if C.lot_date(lot, st) != prod:
                v.append("lot date != production date")
        except Exception:
            v.append("lot unparsed")
    ink = [x for x in q if re.match(r"(BB|USE BY|BEST BY|EXP|BBE) ", x)]
    if ink:
        m = re.match(r"(?:BB|USE BY|BEST BY|EXP|BBE) (.+?)  (.+)$", ink[0])
        if m:
            if pdate(m.group(1), us) != exp:
                v.append("inkjet date != printed date")
            if lot and m.group(2).strip() != lot:
                v.append("inkjet lot != printed lot")
    return True, v


def num(s):
    m = re.match(r"<?([\d,]+(?:\.\d+)?)", s.strip())
    return float(m.group(1).replace(",", "")) if m else None


def check_eu_table(q):
    v = []
    rows = [x.split("|") for x in q if x.count("|") == 3]
    if "Nutrition" not in q or "%RI*" not in q:
        return False, v
    k = q.index("%RI*")
    serv = re.search(r"(\d+(?:\.\d+)?)\s?(?:g|ml)\)?$", q[k - 1])
    if not serv:
        return False, v
    f = float(serv.group(1)) / 100
    vals = {}
    for r in rows:
        if r[0] == "Energy":
            kj = num(r[1]); kjs = num(r[2])
            vals["kj"] = kj
            if abs(kj * f - kjs) > max(3, 0.03 * kj * f): v.append("energy per serving")
            if abs(kjs / 8400 * 100 - num(r[3])) > 1.01: v.append("energy %RI")
        key = {"Fat": "fat", "of which saturates": "sat", "Carbohydrate": "carb", "of which sugars": "sugar", "Fibre": "fibre",
               "Protein": "protein", "Salt": "salt"}.get(r[0])
        if key:
            a, b = num(r[1]), num(r[2])
            vals[key] = 0.0 if r[1].startswith("<") else a
            if r[1].startswith("<") or r[2].startswith("<"):
                continue
            def step(x):
                return (0.01 if x < 1 else 0.1) if key == "salt" else (1 if x >= 10 else 0.1)
            tol = step(a) / 2 * f + step(b) / 2 + 1e-6
            if abs(a * f - b) > tol: v.append("%s per serving" % key)
            if key in R.EU_RI and r[3] != "-":
                if abs(b / R.EU_RI[key] * 100 - num(r[3])) > (step(b) / 2) / R.EU_RI[key] * 100 + 0.51: v.append("%s %%RI" % key)
    if all(k in vals for k in ("kj", "fat", "carb", "protein")):
        calc = 17 * vals["carb"] + 17 * vals["protein"] + 37 * vals["fat"] + 8 * vals.get("fibre", 0)
        if abs(calc - vals["kj"]) > max(25, 0.04 * vals["kj"]): v.append("energy vs macros")
    return True, v


US_DVK = {"Total Fat": "fat", "Saturated Fat": "sat", "Cholesterol": "cholesterol", "Sodium": "sodium", "Total Carbohydrate": "carb_total",
          "Dietary Fiber": "fibre", "Vitamin D": "vitd", "Calcium": "calcium", "Iron": "iron", "Potassium": "potassium"}


def check_us_table(q):
    v = []
    if "Nutrition Facts" not in q:
        return False, v
    vals = {}
    for x in q:
        parts = [p.strip() for p in x.split("|")]
        if parts[0] in US_DVK and len(parts) == 3:
            a, d = num(parts[1]), num(parts[2])
            vals[parts[0]] = a
            exp = a / R.US_DV[US_DVK[parts[0]]] * 100
            tol = max(2.5, 0.12 * exp)
            if abs(exp - d) > tol: v.append("%DV " + parts[0])
        if parts[0] in ("Protein", "Total Sugars") and len(parts) == 2:
            vals[parts[0]] = num(parts[1])
    try:
        cal = num(q[q.index("Calories") + 1])
    except (ValueError, IndexError):
        return True, v
    if all(k in vals for k in ("Total Fat", "Total Carbohydrate", "Protein")):
        fib = vals.get("Dietary Fiber", 0)
        calc = 9 * vals["Total Fat"] + 4 * (vals["Total Carbohydrate"] - fib) + 2 * fib + 4 * vals["Protein"]
        if abs(calc - cal) > max(20, 0.15 * cal): v.append("calories vs macros")
    return True, v


ALLERGEN_KW = {"milk": ["milk", "butter", "cream", "cheese", "whey", "yogurt", "yoghurt", "casein", "lactose", "buttermilk"],
               "wheat": ["wheat", "spelt", "semolina", "durum"], "egg": ["egg"], "soy": ["soya", "soy", "soybean"], "peanut": ["peanut"],
               "almond": ["almond"], "hazelnut": ["hazelnut"], "walnut": ["walnut"], "cashew": ["cashew"], "pistachio": ["pistachio"],
               "sesame": ["sesame", "tahini"], "fish": ["salmon", "cod", "tuna", "anchov", "pollock", "haddock", "fish"],
               "mustard": ["mustard"], "celery": ["celery", "celeriac"]}
EXEMPT = ["yogurt cultures", "yoghurt cultures", "glucose syrup", "maltodextrin", "dextrose", "refined soy", "refined soya", "soybean oil", "tocopherol", "cocoa butter",
          "peanut oil", "buckwheat", "coconut milk", "nutmeg", "butternut", "cream of tartar", "shea", "almond-shaped"]


def check_allergens(q, us):
    v = []
    ing = next((x for x in q if x.startswith("Ingredients: ") or x.startswith("INGREDIENTS: ")), None)
    if not ing:
        return False, v
    low = ing.lower()
    for ex in EXEMPT:
        low = low.replace(ex, "")
    found = {k for k, ws in ALLERGEN_KW.items() if any(re.search(r"\b" + w, low) for w in ws)}
    if not us:
        for k in found:
            ws = ALLERGEN_KW[k]
            caps = any(re.search(r"\b" + w.upper(), ing) for w in ws) or (k == "fish" and "FISH" in ing) or \
                   (k == "wheat" and re.search(r"\bWHEAT|SPELT|GLUTEN", ing))
            if k in ("mustard", "celery", "fish", "sesame") and not caps:
                caps = any(w.upper() in ing for w in ws) or any(x in ing for x in ("SALMON", "COD", "TUNA", "ANCHOV", "POLLOCK"))
            if not caps: v.append("EU allergen not emphasised: " + k)
    else:
        cont = next((x for x in q if x.startswith("CONTAINS:")), "").lower()
        for k in found - {"mustard", "celery"}:
            word = {"egg": "egg", "soy": "soy", "milk": "milk", "wheat": "wheat", "peanut": "peanut", "fish": None}.get(k, k)
            if word and word not in cont: v.append("US contains missing: " + k)
    return True, v


def check_quid_order(q):
    ing = next((x for x in q if x.startswith("Ingredients: ") or x.startswith("INGREDIENTS: ")), None)
    if not ing:
        return False, []
    top = re.split(r",(?![^()]*\))", ing.split(": ", 1)[1])
    pcts = []
    for t in top:
        m = re.search(r"\((\d+(?:\.\d+)?)%\)\s*\.?$", t.strip())
        if m:
            pcts.append(float(m.group(1)))
    big = [p for p in pcts if p >= 2]
    return True, (["QUID percentages not descending"] if any(b > a + 1e-9 for a, b in zip(big, big[1:])) else [])


def yr_for(mon):
    return 2026 if mon >= 10 else 2027


def check_weekdays(text):
    v = []
    n = 0
    for m in re.finditer(r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),? (\d{1,2}) (%s) (\d{4})" % "|".join(C.MON), text):
        n += 1
        d = dt.date(int(m.group(4)), MONF[m.group(3)], int(m.group(2)))
        if d.weekday() != WD[m.group(1)]: v.append("weekday " + m.group(0))
    for m in re.finditer(r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (%s) (\d{1,2}), (\d{4})" % "|".join(C.MON), text):
        n += 1
        d = dt.date(int(m.group(4)), MONF[m.group(2)], int(m.group(3)))
        if d.weekday() != WD[m.group(1)]: v.append("weekday " + m.group(0))
    for m in re.finditer(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun),? (?:(\d{1,2}) (%s)|(%s) (\d{1,2}))\b" % ("|".join(x[:3] for x in C.MON), "|".join(x[:3] for x in C.MON)), text):
        n += 1
        mon = [x[:3] for x in C.MON].index(m.group(3) or m.group(4)) + 1
        day = int(m.group(2) or m.group(5))
        d = dt.date(yr_for(mon), mon, day)
        if d.weekday() != WD3[m.group(1)]: v.append("weekday " + m.group(0))
    return n, v


def check_agenda(q):
    sl = [re.match(r"(\d\d:\d\d)–(\d\d:\d\d)\|", x) for x in q]
    sl = [(m.group(1), m.group(2)) for m in sl if m]
    if len(sl) < 2:
        return False, []
    return True, (["agenda overlap"] if any(b[0] < a[1] for a, b in zip(sl, sl[1:])) else [])


def check_promo(q):
    v = []
    J = " ## ".join(q)
    m = re.search(r"Save (\d+)% ## Now (\D*)([\d,.]+)\D* ## Was \D*([\d,.]+)", J)
    if m:
        pct = int(m.group(1)); now = float(m.group(3).replace(",", "")); was = float(m.group(4).replace(",", ""))
        if abs((1 - now / was) * 100 - pct) > 2.5: v.append("save% math")
    m = re.search(r"Any (\d) for \D*([\d,.]+)\D* ## Single \w+ \D*([\d,.]+)", J)
    if m and float(m.group(2).replace(",", "")) >= int(m.group(1)) * float(m.group(3).replace(",", "")): v.append("multibuy not cheaper")
    hp = re.search(r"(?:Now|Sale|Member price|Flash deal|Final price) \D*?([\d,.]+\d)", J)
    rp = re.search(r" at \D*?([\d,.]+\d), limit", J)
    if hp and rp and hp.group(1) != rp.group(1): v.append("headline price != rules price")
    return bool(re.search(r"Offer valid", J)), v


def check_event_consistency(q, text):
    v = []
    pl = [int(m.group(1)) for x in q for m in [re.match(r"(?:Places|Spots): (\d+)$", x)] if m]
    lim = [int(m.group(1)) for x in q for m in [re.match(r"Limited to (\d+) participants\.$", x)] if m]
    if pl and lim and pl[0] != lim[0]: v.append("places mismatch")
    addrs = [x for x in q if re.search(r"\d", x) and ("," in x) and any(c in x for c in (", USA", ", Canada", ", United Kingdom", ", Ireland")) or False]
    return bool(pl), v


CLAIM_EU = {"Low fat": ("Fat", lambda v, f: v <= (3 if f else 1.5)), "Fat free": ("Fat", lambda v, f: v <= 0.5),
            "Low sugars": ("of which sugars", lambda v, f: v <= (5 if f else 2.5)), "Sugars free": ("of which sugars", lambda v, f: v <= 0.5),
            "Low salt": ("Salt", lambda v, f: v <= 0.3), "High fibre": ("Fibre", lambda v, f, k=0: v >= 6 or (k > 0 and v / k * 100 >= 3)),
            "Source of fibre": ("Fibre", lambda v, f, k=0: v >= 3 or (k > 0 and v / k * 100 >= 1.5))}
CLAIM_US = {"Low fat": ("Total Fat", lambda v: v <= 3), "Fat free": ("Total Fat", lambda v: v < 0.5), "Sugar free": ("Total Sugars", lambda v: v < 0.5),
            "Low sodium": ("Sodium", lambda v: v <= 140)}


def check_claims(q):
    v = []
    n = 0
    rows = {x.split("|")[0].strip(): x.split("|") for x in q if "|" in x}
    solid = any(x.startswith("Per 100g") for x in q)
    for c, (lab, fn) in CLAIM_EU.items():
        if c in q and lab in rows and len(rows[lab]) == 4:
            n += 1
            val = num(rows[lab][1])
            kc = re.search(r"/ (\d+)kcal", rows["Energy"][1]) if "Energy" in rows else None
            ok = fn(val, solid, int(kc.group(1))) if ("fibre" in c and kc) else fn(val, solid) if val is not None else True
            if val is not None and not rows[lab][1].startswith("<") and not ok: v.append("claim " + c)
    for c, (lab, fn) in CLAIM_US.items():
        if c in q and lab in rows and len(rows[lab]) in (2, 3) and "Nutrition Facts" in q:
            n += 1
            val = num(rows[lab][1])
            if val is not None and not fn(val): v.append("claim " + c)
    return n > 0, v


EXAG = re.compile(r"\b(cures?|prevents?|reverses?|clinically proven|FDA approved|licensed medicine|miracle|burns fat|detox(?:es)?)\b", re.I)
RESIDUE = re.compile(r"\{|\}|\bNone\b|TODO|XXX|\bnan\b|\[\]|lorem|\$\{|%s|%d")


def main(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    res = {"n_rows": len(rows), "errors": [], "checks": defaultdict(lambda: Counter())}
    E = res["errors"]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)): E.append("duplicate ids")
    groups = defaultdict(list)
    for r in rows:
        groups[r["group_id"]].append(r)
    for g, rs in groups.items():
        if sorted(r["variant"] for r in rs) != ["clean", "strong", "subtle"]: E.append(g + " variants")
        for k in ("layout", "aspect_ratio", "carrier", "brand_or_organizer", "visual_style", "source_archetype", "country"):
            if len({r[k] for r in rs}) != 1: E.append("%s differs in %s" % (g, k))
        ps = {r["variant"]: r["prompt"] for r in rs}
        if len(set(ps.values())) != 3: E.append(g + " identical prompts")
        if quoted(ps["clean"]) == quoted(ps["subtle"]): E.append(g + " subtle quoted text == clean")
    for r in rows:
        p = r["prompt"]
        if p.count("「") != p.count("」"): E.append(r["id"] + " unbalanced quotes")
        if RESIDUE.search(body(p)): E.append(r["id"] + " residue: " + RESIDUE.search(body(p)).group())
        if r["variant"] == "clean" and r["tamper_types"]: E.append(r["id"] + " clean has tampers")
        for dtl in r["tamper_details"]:   # tamper ground truth must be locatable in the prompt
            for tok in re.findall(r"\bL\d{5}[A-Z]\b|\bL \d{6} [A-Z]\b|\bLOT \d{6}-\d\d\b|\bL\d{8}[A-Z]\b", dtl):
                if tok not in p: E.append("%s tamper detail lot %s not in prompt" % (r["id"], tok))
            for m in re.finditer(r"(?:added|badge|reads|now reads|changed to|replaced by|rewritten as)[^“]{0,25}“([^”]+)”", dtl):
                if m.group(1) not in p: E.append("%s tamper detail text not in prompt: %s" % (r["id"], m.group(1)[:50]))
        if r["variant"] != "clean" and not r["tamper_types"]: E.append(r["id"] + " tampered row without tampers")
        q = [x.strip() for x in quoted(body(p))]
        us = "Nutrition Facts" in q or "Supplement Facts" in q or r["country"] == "US"
        cat = r["super_category"]
        tests = []
        if cat in ("Food label", "Commercial ad", "Supplement"):
            tests += [("dates", check_dates(q, us))]
        if cat in ("Food label", "Commercial ad"):
            tests += [("eu_table", check_eu_table(q)), ("us_table", check_us_table(q)), ("allergens", check_allergens(q, us)),
                      ("quid_order", check_quid_order(q)), ("claims", check_claims(q))]
        if cat == "Commercial ad":
            tests += [("promo", check_promo(q))]
        if cat in ("Event",):
            tests += [("agenda", check_agenda(q)), ("event", check_event_consistency(q, p))]
        nwd, vwd = check_weekdays(" ".join(q))
        tests.append(("weekday", (nwd > 0, vwd)))
        for name, (matched, viol) in tests:
            c = res["checks"][name]
            if matched:
                c["matched_" + r["variant"]] += 1
            if viol:
                c["viol_" + r["variant"]] += 1
                if r["variant"] == "clean":
                    E.append("%s clean %s: %s" % (r["id"], name, "; ".join(viol)))
        # regression checks for review-round-1 defect classes (all variants)
        J = " | ".join(q)
        for pat, name in ((r"\b(\w+\.?) \1\b(?! \d)", "doubled word"), (r"or colder or colder|or below or below", "doubled temperature phrase"),
                          (r"(Made|Produced) in United", "missing 'the'"), (r"Lot: LOT", "Lot: LOT"), (r"\{|\}", "placeholder"),
                          (r"gummys\b|softgelss\b|tabletss\b", "plural typo")):
            mm = re.search(pat, J)
            if mm and not (name == "doubled word" and mm.group(1).lower() in ("that", "had", "very", "no", "bye")):
                E.append("%s %s: %s" % (r["id"], name, mm.group(0)))
        if re.search(r"limit \d+ per customer", J) and re.search(r"one per customer", J):
            E.append(r["id"] + " conflicting purchase limits")
        sv = re.search(r"Per (?:1/(\d)) [a-z]+ \((\d+)(?:g|ml)\)", J)
        net = re.search(r"\b(\d+)(?:g|ml) ℮", J)
        if sv and net and abs(int(net.group(1)) / int(sv.group(1)) - int(sv.group(2))) > 0.07 * int(sv.group(2)):
            E.append(r["id"] + " portion fraction vs net quantity")
        # round-4 review regressions (clean rows only: tampered rows may carry these deliberately)
        if r["variant"] == "clean":
            mp = re.search(r"\b(\d+) x (\d+)(g|ml)\b", J)
            pc = re.search(r"Per 1 [a-z]+ \((\d+)(?:g|ml)\)", J)
            if mp and pc and int(mp.group(1)) > 1 and 0.5 <= int(mp.group(2)) / int(pc.group(1)) <= 2 and int(mp.group(2)) != int(pc.group(1)):
                E.append(r["id"] + " multipack piece weight vs portion")
            ps = re.search(r"Per 1 slice \((\d+)(?:g|ml)\)", J)
            if ps and net and int(ps.group(1)) > 0.5 * int(net.group(1)):
                E.append(r["id"] + " slice larger than half the pack")
            if r["country"] == "CA" and re.search(r"\d°F", J) and not re.search(r"\d°C", J):
                E.append(r["id"] + " Canadian row with Fahrenheit only")
            if r["country"] == "CA" and re.search(r"USDA|FoodSafety\.gov|\bFDA\b", J):
                E.append(r["id"] + " Canadian row cites US agency")
            fam = re.search(r"Price is per (\w+)", J)
            if fam and re.search(r"per person", J) and fam.group(1) != "person":
                E.append(r["id"] + " ticket basis contradicts rules")
            if r["country"] == "US" and "naturally contain sugars" in J:
                E.append(r["id"] + " EU juice statement on US label")
            sup = re.search(r"(\d+)-month", J)
            cntm = re.search(r"\b(\d+) (?:tablets|capsules|softgels|gummies)\b", J)
            dose = re.search(r"Take (\d|one|two|three) (?:tablets?|capsules?|softgels?|gummies) (?:daily|a day|per day)", J, re.I)
            if sup and cntm and dose:
                d = {"one": 1, "two": 2, "three": 3}.get(dose.group(1).lower(), None) or int(dose.group(1))
                if abs(int(cntm.group(1)) / d - 30 * int(sup.group(1))) > 3 * int(sup.group(1)):
                    E.append(r["id"] + " N-month supply vs count/dose")
        # round-5 review regressions
        if r["super_category"] == "Event" and re.search(r"no booking|walk in|just drop|just come|drop by", J, re.I) and re.search(r"Limited to \d+ participants", J):
            E.append(r["id"] + " drop-in event with participant cap")
        if r["super_category"] == "Event" and r["variant"] == "clean" and re.search(r"(25 December|December 25|Dec 25|1 January|January 1\b|Jan 1\b)", J):
            if re.search(r"When: [^|]*(\b25 December|December 25\b|Dec 25\b|\b1 January|January 1\b|Jan 1\b)", J):
                E.append(r["id"] + " event on Christmas Day / New Year's Day")
        if r["super_category"] == "Supplement" and r["country"] != "US" and r["variant"] == "subtle" and any(d.startswith("Allergen statement") and "badge" not in d for d in r["tamper_details"]):
            ing = next((x for x in q if x.startswith("Ingredients")), "")
            if re.search(r"\b(MILK|SOYA|FISH|EGGS?|WHEAT|GLUTEN|PEANUTS?|NUTS|SESAME|CRUSTACEANS|MOLLUSCS|CELERY|MUSTARD|LUPIN|SULPHITES)\b", ing):
                E.append(r["id"] + " allergen deletion leaves CAPITALS emphasis")
        if r["super_category"] == "Event" and not re.search(r"pharm|health", r["source_archetype"]):
            wh = next((x for x in q if x.startswith("Where:")), "")
            if re.search(r"pharm|farmac|apothe|apotek|apteka|aptiek|lékárna", wh.split(",")[0], re.I) and not re.search(r"pharmacy", ",".join(wh.split(",")[1:]), re.I):
                E.append(r["id"] + " pharmacy venue for non-health event")
        if "1 serving per container" in q and r["variant"] == "clean":
            nl = next((x for x in q if x.startswith("NET WT")), "")
            mnet = list(re.finditer(r"(\d+)g\b", nl))
            mnet = mnet[-1] if mnet else None
            msv = next((re.search(r"\((\d+)(?:g|mL)\)", x) for x in q if re.search(r"^\S.*\(\d+(g|mL)\)$", x) and "NET" not in x), None)
            if mnet and msv and abs(int(mnet.group(1)) - int(msv.group(1))) > 0.1 * int(mnet.group(1)):
                E.append(r["id"] + " single serving != net")
        if r["variant"] == "clean" and cat != "Public-service poster":
            m = EXAG.search(" ".join(x for x in q if not re.search(r"not been evaluated by the Food and Drug|may not claim|not intended to|cannot|can't|do not", x, re.I)))
            if m: E.append("%s clean exaggeration word: %s" % (r["id"], m.group()))
    # duplicates: 6-gram Jaccard on quoted text per category
    def grams(p):
        w = re.findall(r"[a-z0-9]+", " ".join(quoted(body(p))).lower())
        return {" ".join(w[i:i + 6]) for i in range(len(w) - 5)}
    dup = {}
    for cat in sorted({r["super_category"] for r in rows}):
        cl = [r for r in rows if r["super_category"] == cat and r["variant"] == "clean"]
        G = [grams(r["prompt"]) for r in cl]
        js = []
        for i in range(len(G)):
            for j in range(i + 1, len(G)):
                u = len(G[i] | G[j])
                js.append(len(G[i] & G[j]) / u if u else 0)
        js.sort()
        if js:
            dup[cat] = {"pairs": len(js), "median": round(js[len(js) // 2], 3), "p99": round(js[int(len(js) * 0.99)], 3), "max": round(js[-1], 3)}
    res["dup_6gram_jaccard_clean"] = dup
    res["exact_duplicate_prompts"] = len(rows) - len({r["prompt"] for r in rows})
    res["density"] = Counter(r["text_density"] for r in rows)
    res["checks"] = {k: dict(v) for k, v in res["checks"].items()}
    out = os.path.splitext(path)[0] + "_qa.json"
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("rows", len(rows), "errors", len(E))
    for e in E[:60]:
        print("  -", e)
    print(json.dumps(res["checks"], indent=0)[:3000])
    print("dup", dup, "exact dups", res["exact_duplicate_prompts"], "density", dict(res["density"]))


if __name__ == "__main__":
    main(sys.argv[1])
