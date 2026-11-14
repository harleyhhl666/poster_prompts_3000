"""Prompt renderers for food labels and commercial ads."""
import common_en as C
import food_en as F
import promo_en as P
import visual_en as V


def Q(s):
    return "「%s」" % s


def QL(lines, sep="; "):
    return sep.join(Q(x) for x in lines if x)


def tail(variant, tampers, kind, table=True, caps=False):
    out = []
    if variant == "clean":
        out.append(V.CLEAN_NOTE)
    else:
        f = list(dict.fromkeys(V.FIELD_NAMES[t["type"]] for t in tampers))
        out.append(V.TAMPER_NOTE.format(fields=", ".join(f), kind=kind))
    out.append(V.QUOTE_RULE + " " + V.TEXT_RULE + (" " + V.TABLE_RULE if table else "") + (" " + V.CAPS_RULE if caps else "") + " " + V.FONT_RULE)
    return "\n".join(out)


def nutrition_block(sp):
    t = sp["table"]
    if t["kind"] == "EU":
        head = "Nutrition table with header row %s, %s, %s, %s; rows: " % (Q("Nutrition"), Q("Per 100g" if sp["form"] == "solid" else "Per 100ml"),
                                                                           Q("Per %s" % t["serv_label"]), Q("%RI*"))
        rows = "; ".join(Q("|".join(r)) for r in t["rows"])
        return head + rows + "; footnote " + Q("*Reference intake of an average adult (8400kJ/2000kcal)") + "."
    rows = "; ".join(Q("|".join(x for x in r if x != "") if r[2] else "|".join(x for x in r[:2] if x)) for r in t["rows"])
    return ("US-style Nutrition Facts panel (black rules, bold headings): %s; %s; %s %s; %s; %s %s; %s; rows: %s; footnote %s." % (
        Q("Nutrition Facts"), Q(F.servings_text(sp["servings"])), Q("Serving size"), Q("%s (%dg)" % (t["household"], sp["serv_g"]) if sp["form"] == "solid" else "%s (%dmL)" % (t["household"], sp["serv_g"])),
        Q("Amount per serving"), Q("Calories"), Q(str(t["calories"])), Q("% Daily Value*"), rows,
        Q("*The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.")))


def front_lines(sp):
    L = [sp["name"], sp["legal"]]
    if sp["headline_extra"]:
        L.append(sp["headline_extra"])
    L += sp["claims"] + sp["front_claims"]
    if sp["health_claim"]:
        L.append(sp["health_claim"])
    if sp["quid_front"]:
        L.append(sp["quid_front"])
    if sp["attr"]:
        L.append(sp["attr"])
    if sp["free_from"]:
        L.append(sp["free_from"])
    L += sp["selling"]
    L.append(sp["origin_badge"])
    L.append(sp["net_front"])
    return L


def info_lines(sp):
    L = [F.ingredients_text(sp)] + F.allergen_lines(sp)
    L.append(sp["storage"])
    if sp["prep"]:
        L.append(sp["prep"])
    if sp["population"]:
        L.append(sp["population"])
    return L


def back_tail_lines(sp):
    L = F.date_lines(sp) + F.producer_lines(sp) + [F.care_line(sp), ("Net quantity: " if sp["regime"] == "EU" else "") + sp["net_back"]]
    return L


LABEL_CARRIERS = [("back_flat", 3), ("front_back", 3), ("bottle_wrap", 2), ("can_tin", 2), ("carton_side", 2), ("freezer", 2), ("handheld", 2)]
CARRIER_DESC = {
    "back_flat": ("a {pack} laid flat showing its back label, with a second, smaller view of its front panel placed above it", ["4:5", "3:4", "1:1"]),
    "front_back": ("the front and back panels of the same {pack} side by side", ["16:9", "4:3"]),
    "bottle_wrap": ("a wrap-around label on a {pack}, shown in two views (front and back) side by side", ["4:3", "16:9"]),
    "can_tin": ("a {pack} shown front and back side by side, label wrapping the cylinder", ["4:3", "16:9"]),
    "carton_side": ("a {pack} at a three-quarter angle so the front and the information side panel are both readable", ["4:5", "1:1"]),
    "freezer": ("a frozen {pack} lying in a supermarket chest freezer, back panel facing up", ["4:5", "3:4"]),
    "handheld": ("two smartphone shots side by side in a supermarket aisle: the front of a {pack} on the shelf, and the same {pack} held in a shopper's hand turned to show the back label", ["16:9", "4:3"])}


def label_prompt(sp, g, variant, tampers):
    cd, _ = CARRIER_DESC[g["carrier"]]
    scene = cd.format(pack=sp["pack"]["pack"])
    out = ["Create a %s image of %s. %s." % (g["ar"], scene, V.REALISM[g["realism"]].capitalize()),
           "Visual style: %s; background and props palette: %s (the package itself keeps the look described here). Fictional brand %s, product %s; packaging look: %s." % (
               g["style"], V.PALETTES[g["palette"]], Q(sp["brand"]), Q(sp["name"]), sp["visual"])]
    lay = g["layout"]
    out.append("[Front panel / main face] " + QL(front_lines(sp)) + ".")
    out.append("[Back panel, %s] " % lay + QL(info_lines(sp)) + ".")
    out.append("[Nutrition] " + nutrition_block(sp))
    out.append("[Date and origin block] " + QL(back_tail_lines(sp)) + ".")
    out.append("[Inkjet code printed in black dot-matrix on %s] %s." % (sp["ink_place"], Q(F.inkjet_text(sp))))
    out.append("[Barcode] %s barcode with the digits %s beneath it." % ("a UPC-A" if sp["regime"] == "US" else "an EAN-13", Q(sp["barcode"])))
    if g["artifacts"]:
        out.append("Realism details: " + "; ".join(V.ARTIFACTS[a] for a in g["artifacts"]) + ". All text areas must stay sharp and readable.")
    out.append(tail(variant, tampers, "retail food package", table=True, caps=sp["regime"] == "EU"))
    return "\n".join(out)


# ------------------------------------------------------------------ ads
# only carriers on which a full ingredient list + nutrition table is realistic (reviewers flagged A-frames,
# shelf-edge labels and window posters carrying full label text)
AD_CARRIERS = [
    ("product_info_poster", "an A2 in-store product information and offer poster mounted on a stand next to the shelf in a {retailer} store in {city}", ["3:4", "4:5"], "scene"),
    ("ecommerce", "a long mobile product page of the {retailer} online grocery shop", ["9:16"], "flat"),
    ("app_deal", "a flash-deal product screen of the {retailer} grocery delivery app", ["9:16"], "flat"),
    ("launch", "a new-product launch poster for {retailer} with a product facts panel", ["4:5", "3:4"], "flat"),
    ("sampling_stand", "a printed poster on the front of a tasting/sampling counter in a {retailer} store in {city}", ["3:4", "4:5"], "phone"),
    ("desktop_page", "a desktop web shop product page of {retailer} with the offer banner", ["16:9", "4:3"], "flat")]


def ad_prompt(sp, p, g, variant, tampers):
    car = g["carrier"]
    desc = g["carrier_desc"].format(city=g["city"], retailer=g["retailer"])
    out = ["Create a %s image: %s. %s." % (g["ar"], desc, V.REALISM[g["realism"]].capitalize())]
    if g.get("en_context"):
        out[0] += " Context: %s, so all text is in English." % g["en_context"]
    out.append("Visual style: %s; layout palette: %s (the product pack keeps its own look: %s). Fictional retailer %s promoting fictional brand %s." % (
        g["style"], V.PALETTES[g["palette"]], sp["visual"], Q(g["retailer"]), Q(sp["brand"])))
    head = [g["theme"]] if g.get("theme") else []
    if p.get("headline_extra"):
        head.append(p["headline_extra"])
    out.append("[Top banner] " + QL([g["retailer"]] + head + ["Offer: " + P.period_text(p)]) + ".")
    hero = [sp["name"], sp["net_front"]]
    if sp["headline_extra"]:
        hero.append(sp["headline_extra"])
    hero += sp["claims"] + sp["front_claims"] + ([sp["health_claim"]] if sp["health_claim"] else [])
    hero += [x for x in (sp["quid_front"], sp["attr"], sp["free_from"]) if x] + sp["selling"]
    out.append("[Product hero area] large product photo of the pack with copy: " + QL(hero) + ".")
    unit = sp["pack"]["pack"]
    pb = P.headline(p, unit)
    if p.get("gift"):
        pb.append("FREE gift for the first %d customers" % (p.get("gift_quota") or p["quota"] or 100))
    out.append("[Price block, large] " + QL(pb) + ".")
    info = [F.ingredients_text(sp)] + F.allergen_lines(sp) + F.date_lines(sp) + [sp["storage"]] + F.producer_lines(sp) + [("Net quantity: " if sp["regime"] == "EU" else "") + sp["net_back"]]
    out.append("[Product information box, small print] " + QL(info) + ".")
    out.append("[Nutrition] " + nutrition_block(sp))
    out.append("[Offer rules, small print at the bottom] " + QL(P.rules(p, sp["core"])) + ".")
    if any("scan" in x.lower() or "qr" in x.lower() for x in hero + pb):
        out.append("[QR code] a plain square QR code graphic near the price block (no readable text inside it).")
    if g["artifacts"]:
        out.append("Realism details: " + "; ".join(V.ARTIFACTS[a] for a in g["artifacts"]) + ". All text must stay sharp and readable.")
    out.append(tail(variant, tampers, "retail advertisement", table=True, caps=sp["regime"] == "EU"))
    return "\n".join(out)
