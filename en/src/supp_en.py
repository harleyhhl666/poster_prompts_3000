"""Supplement spec, renderers and tamper ops (US Supplement Facts / EU-UK food supplement)."""
import re

import common_en as C
import rules_en as R
from geo_en import bump_first_number as bump


def T(t, f, d):
    return {"type": t, "field": f, "detail": d}


US_UNIT = {"µg": "mcg", "mg": "mg", "g": "g"}
DSHEA = "*These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease."
IRON_WARN = ("WARNING: Accidental overdose of iron-containing products is a leading cause of fatal poisoning in children under 6. "
             "Keep this product out of reach of children. In case of accidental overdose, call a doctor or poison control center immediately.")
EU_WARN = ["Do not exceed the recommended daily dose.", "Food supplements should not be used as a substitute for a varied and balanced diet and a healthy lifestyle.",
           "Keep out of the reach of young children."]
US_WARN = ["Keep out of reach of children.", "If you are pregnant, nursing, taking any medications or have a medical condition, consult your doctor before use."]


def amt_str(a, reg):
    v = a["amt"]
    u = US_UNIT.get(a["unit"], a["unit"]) if reg == "US" else a["unit"]
    s = ("%g" % v) if v < 1000 else "{:,}".format(int(v))
    return s + " " + u if reg == "US" else s + u


def build(s, gid, market, brand, ref, rng, geo):
    reg = "US" if market == "US" else "EU"
    ni = rng.randrange(len(s["names"]))
    acts = [a for a in s["actives"] if ni in a.get("names", range(len(s["names"])))]
    cnt = rng.choice(s["counts"])
    sp = {"gid": gid, "s": s, "market": market, "regime": reg, "brand": brand, "core": s["names"][ni],
          "name": "%s %s" % (brand, s["names"][ni]), "count": cnt, "sub": s["sub_category"], "price_eur": s["price_eur"]}
    rows = []
    for a in acts:
        k = a.get("nrv_key")
        if k:
            base = R.US_DV[k] if reg == "US" else R.EU_NRV[k]
            p = "{:,}%".format(int(round(a["amt"] / base * 100)))
        else:
            p = "†" if reg == "US" else "**"
        if reg == "US" and k == "folate" and "folic" in a["n"].lower():
            # 21 CFR 101.36: folic acid declared as mcg DFE (1 mcg folic acid = 1.7 mcg DFE) with the folic acid in parentheses
            dfe = a["amt"] * 1.7
            rows.append(["Folate", "%g mcg DFE (%g mcg folic acid)" % (round(dfe), a["amt"]), "{:,}%".format(int(round(dfe / R.US_DV[k] * 100)))])
            continue
        rows.append([a["n"], amt_str(a, reg), p])
    if reg == "US":
        fat = sum(a["amt"] for a in acts if "oil" in a["n"].lower() and a["unit"] == "mg") / 1000.0
        if fat >= 0.5:   # oils supply fat and calories, which Supplement Facts must declare (21 CFR 101.36(b)(2))
            fat_r = round(fat * 2) / 2
            cal = int(round(fat * 9))
            cal = 5 * round(cal / 5) if cal <= 50 else 10 * round(cal / 10)
            top = ([["Calories", str(cal), ""]] if cal >= 5 else []) + [["Total Fat", "%g g" % fat_r, C.pct(fat_r / R.US_DV["fat"] * 100)]]
            rows[:0] = top
        for w in list(s["extra_warnings"]) + list(s["selling"]):
            m = re.search(r"(\d+)\s?mg (?:of )?sodium", w, re.I)
            if m:   # sodium >= 5 mg per serving must be declared in Supplement Facts (21 CFR 101.36(b)(2))
                rows.insert(0, ["Sodium", "%s mg" % m.group(1), C.pct(int(m.group(1)) / R.US_DV["sodium"] * 100)])
                break
    sp["rows"] = rows
    sp["ings"] = [dict(i) for i in s["ingredients"]]
    sp["allergens"] = list(s["allergens"])
    sp["allergen_line_removed"] = False
    sp["free_from"] = None
    ec = list(s["eu_claims"]); rng.shuffle(ec)
    uc = list(s["us_claims"]); rng.shuffle(uc)
    sp["claims"] = (ec[:2] if reg == "EU" else [c + "*" for c in uc[:2]])
    sp["disclaimer"] = DSHEA if (reg == "US" and sp["claims"]) else None
    import food_en as F
    ingtext = " ".join(i["n"] + " " + (i.get("us") or "") for i in s["ingredients"]) + " " + " ".join(a["n"] for a in acts)
    strengths = set(re.findall(r"\d+(?:[.,]\d+)?", s["names"][ni])) | {("%g" % a["amt"]) for a in acts}
    def amt_ok(x):   # e.g. 'Gentle 1mg or 3mg strength' on the 1 mg product
        nums = re.findall(r"(\d+(?:[.,]\d+)?)\s?(?:mg|µg|mcg|iu|billion|g)\b", x, re.I)
        return all(n in strengths for n in nums) and not (nums and re.search(r"\bor\b", x)) and supply_ok(x)
    def supply_ok(x):   # 'N-month supply' must match count / daily dose (review: 60 tablets x 2 a day sold as '3-month value tub')
        m = re.search(r"(\d+)[- ](month|day)", x, re.I)
        if not m and not re.search(r"supply", x, re.I):
            return True
        if not m or s["count_is_net"]:
            return False
        days = cnt / max(1, s["dose"]["units"])
        want = int(m.group(1)) * (30 if m.group(2).lower() == "month" else 1)
        return abs(days - want) <= 0.1 * want
    sel = [x for x in s["selling"] if F.copy_ok(x, ingtext=ingtext, amounts=False) and amt_ok(x)] or list(s["selling"][:2]); rng.shuffle(sel)
    sp["selling"] = sel[:3]
    sp["headline_extra"] = None
    sp["extra_claims"] = []
    has_iron = any(a.get("nrv_key") == "iron" for a in acts)
    base_w = list(EU_WARN) if reg == "EU" else list(US_WARN)
    keys = ("exceed", "reach of", "substitute", "pregnant", "overdose")
    extra = [w for w in s["extra_warnings"] if not any(k in w.lower() and any(k in b.lower() for b in base_w) for k in keys)
             and not (sp.get("allergens") and re.match(r"\s*contains\b", w, re.I))]
    sp["warnings"] = base_w + extra
    if reg == "US" and has_iron and s["form"] in ("tablet", "capsule", "softgel", "chewable tablet", "gummy"):
        sp["warnings"].insert(0, IRON_WARN)
    sp["suitable"] = s["suitable"]
    sp["not_suitable"] = s["not_suitable"]
    sp["directions"] = s["dose"]["directions"]
    sp["dose_units"] = s["dose"]["units"]
    sp["unit_word"] = s["dose"]["unit_word"]
    sp["storage"] = C.us_temps(s["storage"]) if reg == "US" else s["storage"]
    sv, su = s["shelf"]
    sp["shelf"] = [sv, su]
    prod = C.add_days(ref, -rng.randint(20, 160))
    sp["prod"] = prod
    sp["exp"] = C.expiry_of(prod, sv, su)
    sp["date_style"] = rng.choice(C.DATE_STYLES["us" if reg == "US" else "eu"])
    sp["lot_style"] = "LOT YYMMDD-NN" if reg == "US" else rng.choice(C.LOT_STYLES)
    sp["lot_line"] = rng.choice("ABCDEFGHKM")
    sp["lot_nn"] = "%02d" % rng.randint(1, 24)
    sp["lot"] = C.lot_code(prod, sp["lot_style"], sp["lot_line"], sp["lot_nn"])
    sp["ink_lot"] = sp["lot"]
    sp["ink_exp"] = sp["exp"]
    origin = market if rng.random() < 0.6 else rng.choice(["UK", "IE", "DE", "NL", "DK", "CH", "US", "CA", "IT", "PL"])
    sp["origin"] = origin
    sp["producer"] = geo.company(brand, origin, rng, health=True)
    sp["distributor"] = geo.company(brand, market, rng, health=True, importer=True) if origin != market else None
    sp["status_claim"] = None
    sp["attr"] = None
    sp["barcode"] = C.upca(rng) if reg == "US" else C.ean13(rng, C.GS1.get(market, "50"))
    sp["label_type"] = "Dietary Supplement" if reg == "US" else "Food supplement"
    sp["servings"] = (cnt // max(1, sp["dose_units"])) if not s["count_is_net"] else None
    return sp


def d(sp, x):
    return C.fmt_date(x, sp["date_style"])


def ing_line(sp):
    if sp["regime"] == "US":
        acts = {i["n"] for i in sp["s"]["ingredients"] if i.get("active")}
        oth = [i.get("us") or i["n"] for i in sp["ings"] if not i.get("active")]
        return "Other ingredients: " + ", ".join(oth) + "."
    return "Ingredients: " + ", ".join(i["n"] for i in sp["ings"]) + "."


def allergen_line(sp):
    if not sp["allergens"] or sp["allergen_line_removed"]:
        return None
    ws = []
    for t in sp["allergens"]:
        g, _, x = t.partition(":")
        if sp["regime"] == "US":
            w = R.us_allergen_word(t)
            if w:
                ws.append(("Fish (%s)" % x) if g == "fish" else (("Shellfish (%s)" % x) if g == "crustaceans" else w))
        else:
            ws.append({"fish": "FISH", "crustaceans": "CRUSTACEANS", "molluscs": "MOLLUSCS", "milk": "MILK", "soybeans": "SOYA",
                       "eggs": "EGGS", "gluten": "GLUTEN (%s)" % x.upper() if x else "GLUTEN", "nuts": "NUTS", "peanuts": "PEANUTS",
                       "sesame": "SESAME"}.get(g, g.upper()) + (" (%s)" % x if g in ("fish", "crustaceans", "molluscs") and x else ""))
    ws = list(dict.fromkeys(ws))
    if not ws:
        return None
    return ("Contains: " if sp["regime"] == "US" else "Allergy advice: contains ") + ", ".join(ws) + "."


def date_lines(sp):
    if sp["regime"] == "US":
        return ["MFG: " + d(sp, sp["prod"]), "EXP: " + d(sp, sp["exp"]), "Shelf life: " + C.shelf_str(*sp["shelf"]),
            sp["lot"] if sp["lot"].startswith("LOT") else "LOT: " + sp["lot"]]
    return ["Date of manufacture: " + d(sp, sp["prod"]), "Best before: " + d(sp, sp["exp"]), "Shelf life: " + C.shelf_str(*sp["shelf"]),
            sp["lot"] if sp["lot"].startswith("LOT") else "Lot: " + sp["lot"]]


def inkjet(sp):
    return ("EXP %s  %s" if sp["regime"] == "US" else "BBE %s  %s") % (d(sp, sp["ink_exp"]), sp["ink_lot"])


def producer_lines(sp):
    p = sp["producer"]
    L = [("Manufactured by: " if sp["regime"] == "US" else "Manufacturer: ") + "%s, %s." % (p["name"], p["addr"])]
    if sp["distributor"] and not sp.get("dist_removed"):
        q = sp["distributor"]
        L.append(("Distributed by: " if sp["regime"] == "US" else "Distributor: ") + "%s, %s." % (q["name"], q["addr"]))
    return L


def care_line(sp):
    q = sp["distributor"] or sp["producer"]
    return "Customer care: %s, %s. Tel. %s" % (q["name"], q.get("addr_care", q["addr"]), q["phone"])


# ---------------------------------------------------------------- ops
def op_efficacy(sp, level, rng, ctx):
    s = sp["s"]
    if level == "subtle":
        x = rng.choice(s["exag_subtle"])
        sp["selling"][-1] = x
        return T("efficacy_exaggeration", "selling_copy", "Selling line replaced by the over-stated claim \u201c%s\u201d" % x)
    xs = rng.sample(s["exag_strong"], 2)
    sp["headline_extra"] = xs[0]
    sp["extra_claims"].append(xs[1])
    return T("efficacy_exaggeration", "headline", "Disease/cure claims added: \u201c%s\u201d; \u201c%s\u201d" % tuple(xs))


def op_warning(sp, level, rng, ctx):
    w = sp["warnings"]
    if level == "subtle":
        cand = [x for x in w if x.startswith("Do not exceed") or x.startswith("Keep out of") or x.startswith("WARNING")]
        if not cand:
            return None
        x = rng.choice(cand)
        w.remove(x)
        return T("warning_deletion", "warnings", "Mandatory warning deleted: \u201c%s\u201d" % x[:120])
    removed = list(w)
    sp["warnings"] = []
    det = "The whole warnings block deleted (%d statements)" % len(removed)
    if sp["disclaimer"]:
        sp["disclaimer"] = None
        det += " and the FDA disclaimer for the starred claims removed"
    return T("warning_deletion", "warnings", det)


def op_population(sp, level, rng, ctx):
    if level == "subtle":
        if not sp["not_suitable"]:
            return None
        old = sp["not_suitable"]
        sp["not_suitable"] = None
        return T("target_population_tamper", "not_suitable", "Cautionary population statement deleted: \u201c%s\u201d" % old)
    old = sp["not_suitable"]
    sp["not_suitable"] = None
    sp["suitable"] = sp["s"]["pop_tamper"]
    return T("target_population_tamper", "suitable", "Suitability widened to \u201c%s\u201d and the caution \u201c%s\u201d removed" % (sp["suitable"], old))


def op_allergen(sp, level, rng, ctx):
    if not allergen_line(sp):
        return None
    old = allergen_line(sp)
    sp["allergen_line_removed"] = True
    if level == "subtle":
        if sp["regime"] == "EU":
            # EU: CAPITALS in the ingredient list are the mandatory emphasis; deleting only the advice line would leave a
            # compliant label (review round 5), so the emphasis goes too
            import food_en as F
            hit = [i for i in sp["ings"] if re.search(r"\b[A-Z]{3,}\b", re.sub(r"\bE\d+\w*", "", i["n"]))]
            if not hit:
                return None
            for i in hit:
                i["n"] = F.lower_caps(i["n"])
            return T("allergen_deletion", "allergen_statement+ingredients", "Allergen statement \u201c%s\u201d deleted and the CAPITALS emphasis removed from %s, although the product still contains the allergen" % (old, ", ".join("\u201c%s\u201d" % i["n"] for i in hit)))
        return T("allergen_deletion", "allergen_statement", "Allergen statement \u201c%s\u201d deleted although the ingredients still contain it" % old)
    g = sp["allergens"][0].split(":")[0]
    sp["free_from"] = {"fish": "Fish free", "milk": "Dairy free", "soybeans": "Soy free", "crustaceans": "Shellfish free"}.get(g, "Allergen free")
    return T("allergen_deletion", "allergen_statement", "Allergen statement deleted and a conflicting \u201c%s\u201d badge added" % sp["free_from"])


def op_ing_order(sp, level, rng, ctx):
    if sp["regime"] == "US":
        return None  # US label lists only "Other ingredients"; actives are in the facts table
    h = sp["s"]["hero_ing"]
    idx = [k for k, i in enumerate(sp["ings"]) if i["n"] == h]
    if not idx or idx[0] == 0:
        return None
    k = idx[0]
    it = sp["ings"].pop(k)
    if level == "subtle":
        nk = max(0, k - 2)
        sp["ings"].insert(nk, it)
        return T("ingredient_order_tamper", "ingredients", "\u201c%s\u201d (%g mg per dose) moved ahead of ingredients present in larger amounts" % (h, it["mg"]))
    sp["ings"].insert(0, it)
    sp["extra_claims"].append("Main ingredient: " + h.split("(")[0].strip())
    return T("ingredient_order_tamper", "ingredients", "\u201c%s\u201d (%g mg per dose) listed first and promoted as the main ingredient, although it is one of the smallest by weight" % (h, it["mg"]))


def op_shelf(sp, level, rng, ctx):
    tv, tu = sp["s"]["shelf_tamper"]
    old = list(sp["shelf"])
    sp["shelf"] = [tv, tu]
    if level == "subtle":
        return T("shelf_life_tamper", "shelf_life", "Shelf life changed from %s to %s but the expiry date still matches %s" % (C.shelf_str(*old), C.shelf_str(tv, tu), C.shelf_str(*old)))
    oe = sp["exp"]
    sp["exp"] = C.expiry_of(sp["prod"], tv, tu)
    return T("shelf_life_tamper", "expiry", "Shelf life and printed expiry extended (%s -> %s); the inkjet code still shows %s" % (d(sp, oe), d(sp, sp["exp"]), d(sp, sp["ink_exp"])))


def op_prod(sp, level, rng, ctx):
    old = sp["prod"]
    if level == "subtle":
        newp = C.add_days(old, -rng.randint(3, 10))
        sp["prod"] = newp
        sp["exp"] = C.expiry_of(newp, *sp["shelf"])
        sp["ink_exp"] = sp["exp"]
        return T("production_date_tamper", "production_date", "Date of manufacture changed from %s to %s (expiry shifted to match), but the lot code %s still encodes %s" % (d(sp, old), d(sp, newp), sp["lot"], d(sp, old)))
    ref = ctx["ref"]
    gap = (ref - old).days
    newp = C.add_days(old, max(7, int(gap * 0.8)))   # clamped before the display date so only one anomaly type is created
    sp["prod"] = newp
    oe = sp["exp"]
    sp["exp"] = C.expiry_of(newp, *sp["shelf"])
    sp["lot"] = C.lot_code(newp, sp["lot_style"], sp["lot_line"], sp["lot_nn"])
    return T("production_date_tamper", "production_date", "Re-labelled: manufacture date, expiry and lot moved later (%s, %s, %s) while the inkjet code still reads %s %s" % (d(sp, newp), d(sp, sp["exp"]), sp["lot"], d(sp, oe), sp["ink_lot"]))


def op_status(sp, level, rng, ctx):
    if sp["regime"] == "US":
        txt = "FDA approved formula" if level == "subtle" else "FDA approved and clinically licensed to treat deficiency"
        sp["status_claim"] = txt
        return T("regulatory_status_tamper", "status", "False regulatory status \u201c%s\u201d: FDA does not approve dietary supplements before marketing" % txt)
    txt = "Licensed medicine" if level == "subtle" else "Licensed medicine - registered for the treatment of deficiency"
    sp["status_claim"] = txt
    # strong: the 'licensed medicine' claim sits next to the unchanged 'Food supplement' designation -> self-contradictory
    return T("regulatory_status_tamper", "status", "Product labelled as a food supplement also claims \u201c%s\u201d" % txt)


def op_attr(sp, level, rng, ctx):
    a = sp["s"]["attr_tamper"]
    if not a:
        return None
    sp["attr"] = a
    return T("product_attribute_tamper", "attribute", "Unsupported attribute badge \u201c%s\u201d added" % a)


def op_upgrade(sp, level, rng, ctx):
    if not sp["claims"]:
        return None
    up = sp["s"]["upgrade"]
    old = sp["claims"][0]
    new = up[0] if level == "subtle" else up[-1]
    sp["claims"][0] = new + ("*" if sp["regime"] == "US" else "")
    return T("function_upgrade", "claims", "Permitted claim \u201c%s\u201d rewritten as \u201c%s\u201d" % (old.rstrip("*"), new))


def op_unsub(sp, level, rng, ctx):
    xs = sp["s"]["unsub"]
    x = xs[0] if level == "subtle" else xs[-1]
    sp["extra_claims"].append(x)
    return T("unsubstantiated_claim", "claims", "Unsubstantiated proof claim added: \u201c%s\u201d" % x)


def op_nutrition(sp, level, rng, ctx):
    rows = [r for r in sp["rows"] if r[2] not in ("†", "**", "") and "DFE" not in r[1] and r[0] not in ("Total Fat", "Sodium")]
    if not rows:
        return None
    r = rng.choice(rows)
    old = r[1]
    m = re.match(r"([\d.,]+)", old)
    v = float(m.group(1).replace(",", ""))
    nv = v * (2 if level == "subtle" else 4)
    r[1] = old.replace(m.group(1), ("%g" % nv) if nv < 1000 else "{:,}".format(int(nv)), 1)
    return T("nutrition_value_tamper", "facts_table", "%s amount changed from %s to %s while %s stayed %s" % (r[0], old, r[1], "%DV" if sp["regime"] == "US" else "%NRV", r[2]))


def op_manufacturer(sp, level, rng, ctx):
    q = sp["distributor"] or sp["producer"]
    if level == "subtle":
        new, n, nn = bump(q["addr"], 2)
        if new is None:
            return None
        q["addr_care"] = new
        return T("manufacturer_info_tamper", "address", "Customer-care address gives house number %d while the %s line on the same label gives %d" % (nn, "distributor" if sp["distributor"] else "manufacturer", n))
    if sp["distributor"]:
        sp["dist_removed"] = True
        sp["made_in_claim"] = "Made in " + C.the(ctx["country_name"](sp["market"]))
        return T("manufacturer_info_tamper", "origin", "Distributor line removed and \u201c%s\u201d badge added although the manufacturer is in %s" % (sp["made_in_claim"], sp["producer"]["country"]))
    return None


SUPP_OPS = {"efficacy_exaggeration": op_efficacy, "warning_deletion": op_warning, "target_population_tamper": op_population,
            "allergen_deletion": op_allergen, "ingredient_order_tamper": op_ing_order, "shelf_life_tamper": op_shelf,
            "production_date_tamper": op_prod, "regulatory_status_tamper": op_status, "product_attribute_tamper": op_attr,
            "function_upgrade": op_upgrade, "unsubstantiated_claim": op_unsub, "nutrition_value_tamper": op_nutrition,
            "manufacturer_info_tamper": op_manufacturer}
