"""Tamper operators for food specs. op(sp, level, rng, ctx) -> {type, field, detail} | None (mutates sp)."""
import re

import common_en as C
import food_en as F
import rules_en as R
from geo_en import bump_first_number as bump


def T(t, f, d):
    return {"type": t, "field": f, "detail": d}


def op_efficacy(sp, level, rng, ctx):
    a = sp["arc"]
    if level == "subtle":
        x = rng.choice(a["exag_subtle"])
        if sp["selling"]:
            old = sp["selling"][-1]
            sp["selling"][-1] = x
        else:
            sp["selling"].append(x)
        return T("efficacy_exaggeration", "selling_copy", "Selling copy line replaced by the over-stated health claim \u201c%s\u201d" % x)
    xs = rng.sample(a["exag_strong"], 2) if len(a["exag_strong"]) >= 2 else a["exag_strong"]
    sp["headline_extra"] = xs[0]
    if len(xs) > 1:
        sp["selling"].insert(0, xs[1])
    return T("efficacy_exaggeration", "headline", "Medical/absolute health claims added: " + "; ".join("\u201c%s\u201d" % x for x in xs))


def _allergen_ings(sp):
    return [i for i in sp["ings"] if i["a"]]


def op_allergen(sp, level, rng, ctx):
    al = _allergen_ings(sp)
    if not al:
        return None
    if sp["regime"] == "EU":
        if level == "subtle":
            groups = {}
            for i in al:
                for t in i["a"]:
                    groups.setdefault(t.split(":")[0], []).append(i)
            uniq = [i for i in al if any(len(groups[t.split(":")[0]]) == 1 for t in i["a"])]
            i = rng.choice(uniq or al)
            i["emph"] = False
            return T("allergen_deletion", "ingredients", "Allergen emphasis removed from \u201c%s\u201d (now printed as \u201c%s\u201d): the ingredient still contains %s but is no longer highlighted in CAPITALS" % (i["eu"], F.lower_caps(i["eu"]), "/".join(sorted({t.split(':')[0] for t in i['a']}))))
        for i in al:
            i["emph"] = False
        sp["allergy_advice_removed"] = True
        ff = free_from(sp)
        sp["free_from"] = ff
        return T("allergen_deletion", "ingredients+allergy_advice", "All allergen emphasis and the allergy advice line removed, and a conflicting \u201c%s\u201d badge added although the ingredients contain it" % ff)
    words = F.contains_words(sp, include_dropped=True)
    if not words:
        return None
    if level == "subtle":
        if len(words) == 1:
            w = words[0]
        else:
            w = rng.choice(words[1:])
        sp["contains_drop"].add(w)
        rest = [x for x in words if x != w]
        return T("allergen_deletion", "contains_statement", "%s removed from the CONTAINS statement%s although the ingredient list still contains it" % (w, (" (now lists only " + ", ".join(rest) + ")") if rest else " (statement deleted)"))
    for w in words:
        sp["contains_drop"].add(w)
    ff = free_from(sp)
    sp["free_from"] = ff
    return T("allergen_deletion", "contains_statement", "CONTAINS statement deleted and a conflicting \u201c%s\u201d badge added although the ingredients contain %s" % (ff, ", ".join(words)))


def free_from(sp):
    tags = [t for i in sp["ings"] for t in i["a"]]
    g = [t.split(":")[0] for t in tags]
    us = sp["regime"] == "US"
    for key, txt in (("milk", "Dairy free"), ("gluten", "Gluten free"), ("nuts", "Nut free"), ("eggs", "Egg free"),
                     ("soybeans", "Soy free" if us else "Soya free"), ("peanuts", "Peanut free"), ("fish", "Fish free"),
                     ("sesame", "Sesame free"), ("celery", "Allergen free"), ("mustard", "Allergen free")):
        if key in g:
            return txt
    return "Allergen free"


def op_prod_date(sp, level, rng, ctx):
    ref = ctx["ref"]
    sp["prod_tampered"] = True
    if level == "subtle":
        n = rng.randint(3, 10) * rng.choice([1, -1])
        newp = C.add_days(sp["prod"], n)
        if newp > ref:
            newp = C.add_days(sp["prod"], -abs(n))
        old = sp["prod"]
        sp["prod"] = newp
        sp["exp"] = C.expiry_of(newp, *sp["shelf"])
        sp["ink_exp"] = sp["exp"]
        return T("production_date_tamper", "production_date", "Printed production date changed from %s to %s (best-before date and inkjet code shifted to match), but the lot code %s still encodes %s" % (F.d(sp, old), F.d(sp, newp), sp["lot"], F.d(sp, old)))
    old = sp["prod"]
    oldexp = sp["exp"]
    if not ctx.get("inkjet", True):
        newp = C.add_days(ref, rng.randint(10, 40))
        sp["prod"] = newp
        sp["exp"] = C.expiry_of(newp, *sp["shelf"])
        sp["lot"] = C.lot_code(newp, sp["lot_style"], sp["lot_line"], sp["lot_nn"])
        sp["ink_lot"], sp["ink_exp"] = sp["lot"], sp["exp"]
        return T("production_date_tamper", "production_date", "Production date changed from %s to %s (best-before and lot rewritten to match), which is later than the date the offer/poster starts (%s)" % (F.d(sp, old), F.d(sp, newp), F.d(sp, ref)))
    newp = C.add_days(old, max(7, int((ref - old).days * 0.8)))  # clamped before the display date (one anomaly type only)
    sp["prod"] = newp
    sp["exp"] = C.expiry_of(newp, *sp["shelf"])
    sp["lot"] = C.lot_code(newp, sp["lot_style"], sp["lot_line"], sp["lot_nn"])
    det = "Re-labelled: printed production date moved later (%s -> %s), printed %s date and lot rewritten to %s / %s, but the inkjet code on %s still shows %s %s" % (
        F.d(sp, old), F.d(sp, newp), sp["date_kind"].lower(), F.d(sp, sp["exp"]), sp["lot"], sp["ink_place"], F.d(sp, oldexp), sp["ink_lot"])
    return T("production_date_tamper", "production_date", det)


def op_shelf(sp, level, rng, ctx):
    a = sp["arc"]
    tv, tu = a["shelf_tamper"]
    if level == "subtle":
        old = sp["shelf"]
        if tu != old[1]:
            return None
        sp["shelf"] = [tv, tu]
        return T("shelf_life_tamper", "shelf_life", "Stated shelf life changed from %s to %s, but the %s date (%s) still matches the original %s" % (C.shelf_str(*old), C.shelf_str(tv, tu), sp["date_kind"].lower(), F.d(sp, sp["exp"]), C.shelf_str(*old)))
    old = sp["shelf"]
    oldexp = sp["exp"]
    sp["shelf"] = [tv, tu]
    sp["exp"] = C.expiry_of(sp["prod"], tv, tu)
    if not ctx.get("inkjet", True):
        # no inkjet to contradict: push the printed date beyond even the extended shelf life
        sp["exp"] = C.add_months(sp["exp"], 3) if tu == "months" else C.add_days(sp["exp"], max(7, tv // 2))
        det = "Shelf life extended from %s to %s and the %s date moved from %s to %s, which is later than production date + the new shelf life" % (
            C.shelf_str(*old), C.shelf_str(tv, tu), sp["date_kind"].lower(), F.d(sp, oldexp), F.d(sp, sp["exp"]))
        if sp["storage_tamper"]:
            sp["storage"] = sp["storage_tamper"]
            det += "; the chilled/frozen storage instruction is replaced by \u201c%s\u201d" % sp["storage_tamper"]
        return T("shelf_life_tamper", "shelf_life+date", det)
    # printed panel extended consistently, but the inkjet code keeps the original date -> detectable
    det = ("Shelf life extended from %s to %s and the printed %s date moved from %s to %s, while the inkjet code still shows %s") % (C.shelf_str(*old), C.shelf_str(tv, tu), sp["date_kind"].lower(), F.d(sp, oldexp), F.d(sp, sp["exp"]), F.d(sp, sp["ink_exp"]))
    if sp["storage_tamper"]:
        sp["storage"] = sp["storage_tamper"]
        det += "; the chilled/frozen storage instruction is replaced by \u201c%s\u201d" % sp["storage_tamper"]
    return T("shelf_life_tamper", "shelf_life+date", det)


def op_ing_order(sp, level, rng, ctx):
    ings = sp["ings"]
    heroes = [k for k, i in enumerate(ings) if i["hero"] and k > 0 and i["p"] < 30 and i["p"] < ings[0]["p"] * 0.7]
    if not heroes:
        return None
    if level == "subtle":
        withq = [k for k in heroes if ings[k]["quid"] and any(j["quid"] for j in ings[max(0, k - 2):k])]
        k = rng.choice(withq or heroes)
        step = min(k, rng.choice([1, 2]))
        h = ings.pop(k)
        ings.insert(k - step, h)
        jumped = ings[k - step + 1:k + 1]
        sid = bool(h["quid"]) and any(j["quid"] and float(j["quid"]) > float(h["quid"]) for j in jumped)
        return dict(sid=sid, **T("ingredient_order_tamper", "ingredients", "\u201c%s\u201d (recipe share about %.0f%% by weight%s) moved ahead of %s, which are used in larger amounts; the list is no longer in descending order of weight" % (h["eu"], h["p"], "" if h["quid"] else ", not printed", ", ".join("\u201c%s\u201d" % j["eu"] for j in jumped))))
    hs = [ings[k] for k in heroes]
    first = ings[0]
    rest = [i for i in ings if i not in hs and i is not first]
    new = hs + rest[:1] + [first] + rest[1:]
    sp["ings"][:] = new
    h = hs[0]
    claim_pct = min(80, max(30, int(round(max(h["p"] * 2.5, h["p"] + 15) / 5.0)) * 5))
    nm = re.split(r"[(:,]", F.lower_caps(h["eu"]))[0].strip().lower()
    sp["quid_front"] = "Now with %d%% %s" % (claim_pct, nm)
    tail = ("contradicts the %s%% shown in the ingredient list" % h["quid"]) if h["quid"] else "overstates an ingredient whose real share is only %.1f%% by weight" % h["p"]
    return dict(sid=bool(h["quid"]), **T("ingredient_order_tamper", "ingredients+front_quid", "All hero ingredients (%s) moved to the front of the list and the real main ingredient \u201c%s\u201d moved back; front badge \u201c%s\u201d %s" % (", ".join(i["eu"] for i in hs), first["eu"], sp["quid_front"], tail)))


def _row(sp, label):
    for r in sp["table"]["rows"]:
        if r[0].strip().lower() == label.lower():
            return r
    return None


def op_nutrition(sp, level, rng, ctx):
    t = sp["table"]
    if t["kind"] == "EU":
        cands = [r for r in t["rows"] if r[0] in ("Fat", "of which sugars", "of which saturates", "Salt", "Protein", "Carbohydrate") and not r[1].startswith("<")]
        if not cands:
            return None
        if level == "subtle":
            r = rng.choice(cands)
            old = r[1]
            v = float(re.match(r"[\d.]+", old).group())
            nv = v * rng.choice([0.5, 0.6, 1.6, 2.0])
            r[1] = (("%.2f" % nv) if (r[0] == "Salt" and nv < 1) else ("%.1f" % nv if nv < 10 else "%d" % round(nv))) + "g"
            return T("nutrition_value_tamper", "nutrition_table", "%s per 100g changed from %s to %s, while the per-serving value (%s) and %%RI were left unchanged" % (r[0], old, r[1], r[2]))
        ch = []
        for lab in ("Fat", "of which saturates", "of which sugars", "Salt"):
            r = _row(sp, lab)
            if r and not r[1].startswith("<") and not r[2].startswith("<"):
                v = float(re.match(r"[\d.]+", r[1]).group())
                nv = v * 0.3
                old = (r[1], r[2])
                r[1] = (("%.2f" % nv) if (lab == "Salt" and nv < 1) else "%.1f" % nv) + "g"
                v2 = float(re.match(r"[\d.]+", r[2]).group()) * 0.3
                r[2] = (("%.2f" % v2) if (lab == "Salt" and v2 < 1) else "%.1f" % v2) + "g"
                ch.append("%s %s->%s" % (lab, old[0], r[1]))
        if len(ch) < 2:
            return None
        sp["n_tampered"] = True
        return T("nutrition_value_tamper", "nutrition_table", "Several values cut to about 30%% (%s, per 100g and per serving) while energy and %%RI were not changed, so energy no longer matches the macronutrients" % ", ".join(ch))
    rows = {r[0].strip(): r for r in t["rows"]}
    cands = [k for k in ("Total Fat", "Saturated Fat", "Sodium", "Total Sugars", "Protein") if rows[k][1] not in ("0g", "0mg")]
    if not cands:
        return None
    if level == "subtle":
        k = rng.choice([c for c in cands if c != "Total Sugars"] or cands)
        r = rows[k]
        num = float(re.match(r"[\d.]+", r[1]).group())
        unit = "mg" if r[1].endswith("mg") else "g"
        nv = num * rng.choice([0.5, 2.0])
        r[1] = ("%d" % round(nv) if unit == "mg" or nv >= 5 else "%g" % (round(nv * 2) / 2)) + unit
        return T("nutrition_value_tamper", "nutrition_facts", "%s changed from %s%s to %s while its %%DV (%s) was left unchanged" % (k, ("%g" % num), unit, r[1], r[2]))
    ch = []
    for k in ("Total Fat", "Saturated Fat", "Sodium", "Total Sugars"):
        r = rows[k]
        num = float(re.match(r"[\d.]+", r[1]).group())
        if num == 0:
            continue
        unit = "mg" if r[1].endswith("mg") else "g"
        nv = num * 0.3
        old = r[1]
        r[1] = ("%d" % round(nv) if unit == "mg" or nv >= 5 else "%g" % (round(nv * 2) / 2)) + unit
        ch.append("%s %s->%s" % (k, old, r[1]))
    if len(ch) < 2:
        return None
    return T("nutrition_value_tamper", "nutrition_facts", "Several amounts cut to about 30%% (%s) while Calories and %%DV were not changed" % ", ".join(ch))


CONFLICT = {"EU": [("Low fat", "Fat", lambda v, f: v > (3 if f == "solid" else 1.5)), ("Low sugars", "of which sugars", lambda v, f: v > (5 if f == "solid" else 2.5)),
                   ("Sugars free", "of which sugars", lambda v, f: v > 0.5), ("Low salt", "Salt", lambda v, f: v > 0.3),
                   ("High protein", "Protein", None), ("High fibre", "Fibre", lambda v, f: v < 6)],
            "US": [("Low fat", "Total Fat", lambda v, f: v > 3), ("Fat free", "Total Fat", lambda v, f: v >= 0.5),
                   ("Sugar free", "Total Sugars", lambda v, f: v >= 0.5), ("Low sodium", "Sodium", lambda v, f: v > 140)]}


def op_claim(sp, level, rng, ctx):
    reg = sp["regime"]
    rows = {r[0].strip(): r for r in sp["table"]["rows"]}
    ok = []
    for claim, lab, bad in CONFLICT[reg]:
        if claim in sp["claims"] or lab not in rows:
            continue
        cell = rows[lab][1]
        if cell.startswith("<") or not re.match(r"[\d.]+", cell):
            continue
        v = float(re.match(r"[\d.]+", cell).group())
        if claim == "High protein":
            kcal = sp["kcal"]
            if kcal <= 0 or 4 * v / kcal * 100 >= 20:
                continue
        elif not bad(v, sp["form"]):
            continue
        ok.append((claim, lab, cell))
    if not ok:
        return None
    soft = [o for o in ok if o[0] in ("Low sugars", "Low fat", "Low salt", "Low sodium", "High fibre")]
    claim, lab, cell = rng.choice(soft or ok) if level == "subtle" else rng.choice(ok)
    sp["front_claims"].append(claim)
    basis = "per 100g/100ml" if reg == "EU" else "per serving"
    return T("claim_nutrition_conflict", "nutrient_claim", "Front claim \u201c%s\u201d added, but the table shows %s %s (%s), which does not meet the condition for that claim" % (claim, lab.replace("of which ", ""), cell, basis))


def op_quantity(sp, level, rng, ctx):
    pk = sp["pack"]
    unit = "g" if sp["form"] == "solid" else "ml"
    if sp["regime"] == "US" and pk["count"] == 1 and level == "subtle":
        o = C.oz(pk["net"]) if unit == "g" else C.floz(pk["net"])
        wrong = o * 1.12
        old = sp["net_front"]
        sp["net_front"] = old.replace(C._n1(o), C._n1(wrong), 1)
        if sp["net_front"] == old:
            return None
        return T("quantity_tamper", "net_quantity", "Front net quantity reads %s: the ounce figure no longer matches the metric amount (%d%s = %s %s)" % (sp["net_front"], pk["net"], unit, C._n1(o), "OZ" if unit == "g" else "FL OZ"))
    if pk["count"] > 1:
        old = sp["net_front"]
        sp["net_front"] = old.replace("%d x" % pk["count"], "%d x" % (pk["count"] + rng.choice([1, 2])), 1)
        return T("quantity_tamper", "count", "Front pack count changed to \u201c%s\u201d while the back panel still states \u201c%s\u201d" % (sp["net_front"], sp["net_back"]))
    bigger = int(round(pk["net"] * rng.choice([1.2, 1.25, 1.5]) / 10.0) * 10)
    old = sp["net_front"]
    sp["net_front"] = old.replace(str(pk["net"]), str(bigger), 1) if str(pk["net"]) in old else old
    if sp["net_front"] == old:
        return None
    return T("quantity_tamper", "net_quantity", "Front net quantity changed to \u201c%s\u201d while the back panel still states \u201c%s\u201d" % (sp["net_front"], sp["net_back"]))


def op_batch(sp, level, rng, ctx):
    if sp.get("prod_tampered"):
        return None   # the production-date op already rewrote the lot; a second lot edit would falsify its tamper_details
    old = sp["ink_lot"]
    if level == "subtle" and ctx.get("inkjet", True):
        digits = [k for k, ch in enumerate(old) if ch.isdigit()]
        k = digits[-1]
        nd = str((int(old[k]) + rng.randint(1, 8)) % 10)
        sp["ink_lot"] = old[:k] + nd + old[k + 1:]
        return T("batch_number_tamper", "lot_code", "Inkjet lot code reads %s but the printed panel lot is %s (one digit differs)" % (sp["ink_lot"], sp["lot"]))
    nd = C.add_days(sp["prod"], rng.choice([-40, -25, 30, 45]))
    sp["lot"] = C.lot_code(nd, sp["lot_style"], sp["lot_line"], sp["lot_nn"])
    sp["ink_lot"] = sp["lot"]
    return T("batch_number_tamper", "lot_code", "Lot code %s encodes %s, which contradicts the production date %s" % (sp["lot"], F.d(sp, nd), F.d(sp, sp["prod"])))


def op_manufacturer(sp, level, rng, ctx):
    p = sp["producer"]
    if level == "subtle":
        who = sp["importer"] or p
        new, n, nn = bump(who["addr"], rng.choice([2, 4, 6, 10]))
        if new is None:
            return None
        who["addr_care"] = new
        return T("manufacturer_info_tamper", "address", "Customer-care address gives house number %d while the producer/importer address on the same label gives %d" % (nn, n))
    others = [c for c in ("PL", "ES", "NL", "DE", "IT", "UK", "US", "CA", "IE") if c not in (sp["origin"],)]
    fake = rng.choice(others)
    sp["origin_badge"] = ("Made in " if fake in ("US", "CA", "UK") else "Product of ") + C.the(F.COUNTRY_NAME.get(fake, fake))
    det = "Front origin badge \u201c%s\u201d contradicts the producer address in %s" % (sp["origin_badge"], p["country"])
    if sp["importer"]:
        sp["importer_removed"] = True
        det += "; the importer line was also removed"
    return T("manufacturer_info_tamper", "origin", det)


def op_storage(sp, level, rng, ctx):
    if not sp["storage_tamper"]:
        return None
    old = sp["storage"]
    sp["storage"] = sp["storage_tamper"]
    return T("storage_condition_tamper", "storage", "Storage instruction for a chilled/frozen product changed to \u201c%s\u201d (original: \u201c%s\u201d)" % (sp["storage_tamper"], old))


def op_attr(sp, level, rng, ctx):
    a = sp["arc"]["attr_tamper"]
    if not a:
        return None
    sp["attr"] = a
    det = "Unsupported attribute badge \u201c%s\u201d added (no certification or supporting information on the pack)" % a
    if level == "strong":
        sp["front_claims"].append("Certified %s quality" % a.lower() if a.lower() == "organic" else "Officially certified: %s" % a)
        det += " plus a claim of official certification"
    return T("product_attribute_tamper", "attribute", det)


def op_population(sp, level, rng, ctx):
    pop = sp["population"]
    if not pop:
        return None
    if level == "subtle":
        sp["population"] = None
        return T("target_population_tamper", "population", "Age/population line \u201c%s\u201d deleted" % pop)
    sp["population"] = "Suitable for all ages, including babies from birth"
    return T("target_population_tamper", "population", "Age line \u201c%s\u201d replaced by \u201c%s\u201d" % (pop, sp["population"]))


def op_warning(sp, level, rng, ctx):
    s = sp["storage"]
    m = re.search(r"(Once opened[^.]*\.|After opening[^.]*\.|Once thawed[^.]*\.|Do not refreeze[^.]*\.)", s, flags=re.I)
    if not m:
        return None
    sp["storage"] = (s[:m.start()] + s[m.end():]).strip()
    sp["warning_removed"].append(m.group(1))
    return T("warning_deletion", "storage_warning", "Safety instruction \u201c%s\u201d deleted from the storage text" % m.group(1).strip())


FOOD_OPS = {"efficacy_exaggeration": op_efficacy, "allergen_deletion": op_allergen, "production_date_tamper": op_prod_date,
            "shelf_life_tamper": op_shelf, "ingredient_order_tamper": op_ing_order, "nutrition_value_tamper": op_nutrition,
            "claim_nutrition_conflict": op_claim, "quantity_tamper": op_quantity, "batch_number_tamper": op_batch,
            "manufacturer_info_tamper": op_manufacturer, "storage_condition_tamper": op_storage,
            "product_attribute_tamper": op_attr, "target_population_tamper": op_population, "warning_deletion": op_warning}
