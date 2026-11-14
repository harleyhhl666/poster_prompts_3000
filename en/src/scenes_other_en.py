"""Prompt renderers for supplements, events and public-service posters."""
import re

import common_en as C
import eventpsa_en as EP
import supp_en as S
import visual_en as V
from scenes_food_en import Q, QL, tail

SUPP_CARRIERS = [
    ("bottle_label", "a {pack} of {form}s photographed so the full wrap-around label is readable in two views (front and back)", ["4:3", "16:9"], "studio"),
    ("carton_back", "the front and back of a supplement carton side by side", ["16:9", "4:3"], "studio"),
    ("leaflet", "an unfolded A5 product information leaflet lying next to its carton", ["3:4", "4:5"], "studio"),
    ("ecommerce", "a long online-pharmacy product page (English edition) with a close-up photo of the label", ["9:16"], "flat"),
    ("pharmacy_poster", "a shelf poster in a pharmacy in {city} next to the product on display", ["3:4", "4:5"], "scene"),
    ("social_card", "a social-commerce product card for a live-shopping stream, with the product photo and a label close-up", ["9:16", "4:5"], "flat")]


def plural(w):
    return w[:-1] + "ies" if w.endswith("y") else w + "s"


def qr_line(texts):
    if any(re.search(r"\bscan|\bQR\b", x or "", re.I) for x in texts):
        return "[QR code] a plain square QR code graphic beside the call to action (no readable text inside it)."
    return None


def facts_block(sp):
    if sp["regime"] == "US":
        rows = "; ".join(Q("|".join(r)) for r in sp["rows"])
        foot = [Q("† Daily Value not established.")] if any(r[2] == "†" for r in sp["rows"]) else []
        return "Supplement Facts panel (standard FDA layout): %s; %s; %s; header %s; rows: %s%s." % (
            Q("Supplement Facts"), Q("Serving Size %d %s" % (sp["dose_units"], sp["unit_word"].title())),
            Q("Servings Per Container %d" % sp["servings"] if sp["servings"] else "Servings Per Container: see net quantity"),
            Q("Amount Per Serving|% Daily Value"), rows, ("; " + "; ".join(foot)) if foot else "")
    rows = "; ".join(Q("|".join(r)) for r in sp["rows"])
    return "Nutrition information table: header %s; rows: %s; footnotes %s." % (
        Q("Per daily dose (%d %s)|Amount|%%NRV*" % (sp["dose_units"], sp["unit_word"])), rows,
        QL(["*NRV = Nutrient Reference Value"] + (["**No NRV established"] if any(r[2] == "**" for r in sp["rows"]) else [])))


def supp_prompt(sp, g, variant, tampers):
    s = sp["s"]
    desc = g["carrier_desc"].format(pack=s["pack"], form=s["form"], city=g["city"])
    out = ["Create a %s image of %s. %s." % (g["ar"], desc, V.REALISM[g["realism"]].capitalize())]
    if g.get("en_context"):
        out[0] += " Context: %s." % g["en_context"]
    out.append("Visual style: %s; background and layout palette: %s (the product keeps its own look). Fictional brand %s; product look: %s." % (g["style"], V.PALETTES[g["palette"]], Q(sp["brand"]), s["visual"]))
    front = [sp["name"], sp["label_type"]]
    if sp["headline_extra"]:
        front.append(sp["headline_extra"])
    front += [x for x in (sp["status_claim"], sp["attr"], sp["free_from"], sp.get("made_in_claim")) if x]
    front += sp["selling"] + sp["claims"] + sp["extra_claims"]
    front.append("%d %s" % (sp["count"], plural(s["form"])) if not s["count_is_net"] else "Net %d%s" % (sp["count"], "g" if s["form"] == "powder" else "ml"))
    out.append("[Front / main panel] " + QL(front) + ".")
    if g["carrier"] in ("ecommerce", "pharmacy_poster", "social_card"):
        out.append("[Price] " + QL(g["price_lines"]) + ".")
    out.append("[Facts] " + facts_block(sp))
    info = [S.ing_line(sp), S.allergen_line(sp), "Directions: " + sp["directions"], "Suitable for: " + sp["suitable"] if sp["suitable"] else None,
            sp["not_suitable"]] + sp["warnings"] + ([sp["disclaimer"]] if sp["disclaimer"] else []) + ["Storage: " + sp["storage"]]
    out.append("[Information panel] " + QL(info) + ".")
    out.append("[Dates and company] " + QL(S.date_lines(sp) + S.producer_lines(sp) + [S.care_line(sp)]) + ".")
    out.append("[Inkjet code on the base / flap, visible in the image] %s." % Q(S.inkjet(sp)))
    out.append("[Barcode] digits %s." % Q(sp["barcode"]))
    if g["artifacts"]:
        out.append("Realism details: " + "; ".join(V.ARTIFACTS[a] for a in g["artifacts"]) + ". Text stays sharp.")
    out.append(tail(variant, tampers, "supplement product design", table=True))
    return "\n".join(out)


# ------------------------------------------------------------------ events
EVENT_CARRIERS = [("poster", "an A2 event poster", ["3:4", "4:5"], "flat"),
                  ("noticeboard", "an A4 event flyer pinned to a community noticeboard in {city}", ["3:4", "4:5"], "phone"),
                  ("social", "a square social-media event post", ["1:1", "4:5"], "flat"),
                  ("screen", "a digital signage screen in a shopping centre in {city} showing an event announcement", ["9:16", "16:9"], "scene"),
                  ("window", "an event poster displayed in a shop window in {city}", ["3:4", "4:5"], "phone")]


def walkin(sp):
    return bool(re.search(r"no booking|walk in|just drop|just come|drop by", sp["registration"] or "", re.I))


def event_prompt(sp, g, variant, tampers):
    e = sp["e"]
    desc = g["carrier_desc"].format(city=sp["city"]["city"])
    out = ["Create a %s image of %s. %s." % (g["ar"], desc, V.REALISM[g["realism"]].capitalize())]
    if sp["en_context"]:
        out[0] += " Context: %s, so all text is in English." % sp["en_context"]
    out.append("Visual style: %s; palette: %s; motif: %s." % (g["style"], V.PALETTES[g["palette"]], e["visual_motif"]))
    top = [sp["organizer"] + (" presents" if e["commercial"] else ""), sp["title"], sp["subtitle"], sp["fee_text"]]
    if sp["exag"]:
        top.append(sp["exag"])
    out.append("[Header] " + QL(top) + ".")
    info = ["When: " + EP.dates_text(sp), "%s: %s" % (sp["hours_label"], sp["hours"]), "Where: " + sp["venue"], sp["addr"],
            ("Venue capacity: %d" if walkin(sp) else "Places: %d") % sp["quota"]]
    out.append("[Info box] " + QL(info) + ".")
    out.append("[Programme table, two columns time | activity] " + "; ".join(Q("%s|%s" % (EP.fmt_range(a[0], a[1], sp["us"]), a[2])) for a in sp["agenda"]) + ".")
    if sp["speakers"]:
        out.append("[Speakers] " + QL(sp["speakers"]) + ".")
    out.append("[What you get] " + QL(sp["perks"]) + ".")
    # drop-in events cannot cap 'participants'; state a venue capacity instead (review round 5)
    rules = list(sp["rules"]) + ["Entry may pause once %d people are inside." % sp["quota2"] if walkin(sp) else "Limited to %d participants." % sp["quota2"]]
    if sp["fee_rule"]:
        rules.append(sp["fee_rule"])
    out.append("[Good to know, small print] " + QL(rules) + ".")
    foot = ["Register: " + sp["registration"] + (" (%s)" % EP.dates_text(sp, 2) if sp["date2"] else ""), "Info: " + sp["phone"], sp["addr2"]]
    if sp["disclaimer"]:
        foot.append(sp["disclaimer"])
    out.append("[Footer] " + QL(foot) + ".")
    ql = qr_line(top + sp["perks"] + rules + foot)
    if ql:
        out.append(ql)
    if g["artifacts"]:
        out.append("Realism details: " + "; ".join(V.ARTIFACTS[a] for a in g["artifacts"]) + ". Text stays sharp.")
    out.append(tail(variant, tampers, "event poster", table=False))
    return "\n".join(out)


# ------------------------------------------------------------------ PSA
PSA_CARRIERS = [("campaign", "an A2 public-information campaign poster", ["3:4", "4:5"], "flat"),
                ("noticeboard", "a public-information poster in a glass-fronted noticeboard in {city}", ["3:4", "4:5"], "phone"),
                ("infographic", "a long vertical infographic for social media and websites", ["9:16"], "flat"),
                ("leaflet", "the inside spread of an unfolded tri-fold leaflet", ["16:9", "4:3"], "studio"),
                ("transit", "a poster panel in a bus shelter in {city}", ["9:16", "3:4"], "scene"),
                ("canteen", "a poster on the wall of a school or workplace canteen in {city}", ["3:4", "4:5"], "phone")]


def psa_prompt(sp, g, variant, tampers):
    t = sp["t"]
    desc = g["carrier_desc"].format(city=sp["city"]["city"])
    out = ["Create a %s image of %s. %s." % (g["ar"], desc, V.REALISM[g["realism"]].capitalize())]
    if sp["en_context"]:
        out[0] += " Context: %s, so all text is in English." % sp["en_context"]
    out.append("Visual style: %s; palette: %s; illustrations: %s." % (g["style"], V.PALETTES[g["palette"]], t["visual_motif"]))
    out.append("[Header] " + QL([sp["organizer"], "in partnership with " + sp["partner"], sp["title"], sp["subtitle"]]) + ".")
    for k, s in enumerate(sp["sections"]):
        out.append("[Section %d] heading %s; bullet points: %s." % (k + 1, Q(s["heading"]), QL(s["items"])))
    if sp["key_warning"]:
        out.append("[Highlighted warning strip] %s." % Q(sp["key_warning"]))
    ev = sp["event"]
    if ev:
        dd = C.long_date(ev["date"], us=sp["us"])
        if ev["wd_wrong"]:
            dd = dd.replace(C.WEEKDAY[ev["date"].weekday()], C.WEEKDAY[(ev["date"].weekday() + 1) % 7], 1)
        tm = re.findall(r"\d\d:\d\d", ev["time"])
        out.append("[Event box] " + QL(["Free event: " + ev["kind"], dd + ", " + EP.fmt_range(tm[0], tm[1], sp["us"]), ev["venue"] + ", " + ev["addr"], "%d places" % ev["places"]]) + ".")
    cta = [sp["cta"], "Helpline: " + sp["phone"]]
    if ev:
        cta.append("Book one of %d places by phone%s" % (ev["places2"] or ev["places"], (" - see you on " + C.long_date(ev["date2"], us=sp["us"])) if ev["date2"] else ""))
    out.append("[Call to action] " + QL(cta) + ".")
    ql = qr_line(cta)
    if ql:
        out.append(ql)
    foot = ["%s %s" % (sp["emergency_label"], sp["emergency"]), "Questions? Call %s" % sp["phone2"], sp["source"], sp["ref"]]
    out.append("[Footer, small print] " + QL(foot) + ".")
    if g["artifacts"]:
        out.append("Realism details: " + "; ".join(V.ARTIFACTS[a] for a in g["artifacts"]) + ". Text stays sharp.")
    out.append(tail(variant, tampers, "public-information poster", table=False))
    return "\n".join(out)
