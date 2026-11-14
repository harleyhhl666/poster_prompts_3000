"""Event-poster and public-service-poster specs + tamper ops."""
import datetime as dt
import re

import common_en as C
import geo_en as GE
import lib_names_en as N

STORE_KW = r"supermarket|store|shop|aisle|caf[eé]|pharmacy|bakery|deli|atrium|shopping|food hall|concourse|roastery|chocolatier|showroom|counter|checkout|entrance"


def t12(hm):
    h, m = map(int, hm.split(":"))
    return "%d:%02d %s" % ((h - 1) % 12 + 1, m, "am" if h < 12 else "pm")


def fmt_range(a, b, us):
    return ("%s–%s" % (t12(a), t12(b))) if us else "%s–%s" % (a, b)


INDOOR_KW = r"hall|centre|center|library|room|school|campus|church|club|kitchen|studio|lounge|theatre|auditorium|gym|clinic|office|union|college|university"


def venue_for(e, country, rng, cty, title="", brand=""):
    vt = rng.choice(e["venue_types"])
    if brand and re.search(r"\bat " + re.escape(brand), title):
        return "%s, %s" % (brand, vt)  # the title names the organiser's own premises
    if not re.search(STORE_KW, vt, re.I) and not re.search(INDOOR_KW, vt, re.I):
        return "%s, %s" % (vt[0].upper() + vt[1:], cty["city"].split(",")[0])   # outdoor: square, street, park, market
    if re.search(STORE_KW, vt, re.I):
        rk = country if country in ("UK", "IE", "US", "CA") else "EU"
        PH = r"pharm|farmac|apothe|apotek|apteka|aptiek|lékárna|lekarna|chemist|drogist|drogerie"
        shops = [r for r in N.RETAILERS[rk] if bool(re.search(PH, r, re.I)) == bool(re.search(PH, vt, re.I))] or N.RETAILERS[rk]
        return "%s %s, %s" % (rng.choice(shops), cty["city"].split(",")[0], vt)
    return GE.venue(country, rng)

W0, W1 = dt.date(2026, 10, 1), dt.date(2027, 4, 30)
_E = C.easter(2027)
SEASON = {"any": (W0, W1), "autumn": (dt.date(2026, 10, 1), dt.date(2026, 11, 30)), "winter": (dt.date(2026, 12, 1), dt.date(2027, 2, 28)),
          "spring": (dt.date(2027, 3, 1), W1), "halloween": (dt.date(2026, 10, 20), dt.date(2026, 10, 31)),
          "ca_thanksgiving": (dt.date(2026, 10, 1), C.nth_weekday(2026, 10, 0, 2)),
          "us_thanksgiving": (dt.date(2026, 11, 9), C.nth_weekday(2026, 11, 3, 4)),
          "black_friday": (C.nth_weekday(2026, 11, 3, 4), C.add_days(C.nth_weekday(2026, 11, 3, 4), 4)),
          "st_martin": (dt.date(2026, 11, 4), dt.date(2026, 11, 11)), "sinterklaas": (dt.date(2026, 11, 20), dt.date(2026, 12, 5)),
          "christmas_market": (dt.date(2026, 11, 26), dt.date(2026, 12, 23)), "christmas": (dt.date(2026, 12, 1), dt.date(2026, 12, 24)),
          "new_year": (dt.date(2026, 12, 27), dt.date(2027, 1, 6)), "veganuary": (dt.date(2027, 1, 2), dt.date(2027, 1, 31)),
          "burns_night": (dt.date(2027, 1, 18), dt.date(2027, 1, 25)), "valentines": (dt.date(2027, 2, 1), dt.date(2027, 2, 14)),
          "carnival": (dt.date(2027, 2, 1), C.add_days(_E, -48)), "pancake_day": (C.add_days(_E, -53), C.add_days(_E, -47)),
          "mothers_day_uk": (C.add_days(_E, -31), C.add_days(_E, -21)), "st_patricks": (dt.date(2027, 3, 10), dt.date(2027, 3, 17)),
          "easter": (C.add_days(_E, -18), _E)}
FIXED_DAY = {"pancake_day": C.add_days(_E, -47), "burns_night": dt.date(2027, 1, 25), "st_patricks": dt.date(2027, 3, 17),
             "us_thanksgiving": C.nth_weekday(2026, 11, 3, 4), "ca_thanksgiving": C.nth_weekday(2026, 10, 0, 2),
             "halloween": dt.date(2026, 10, 31), "st_martin": dt.date(2026, 11, 11), "sinterklaas": dt.date(2026, 12, 5),
             "mothers_day_uk": C.add_days(_E, -21)}


def T(t, f, d):
    return {"type": t, "field": f, "detail": d}


def season_start(season, rng, days):
    a, b = SEASON[season]
    b2 = C.add_days(b, -(days - 1))
    if b2 < a:
        b2 = a
    return a + dt.timedelta(days=rng.randint(0, (b2 - a).days))


def round_fee(x_eur, cur):
    v = C.eur_to(x_eur, cur)
    if v >= 20:
        v = float(round(v))
    elif v >= 3:
        v = round(v * 2) / 2
    return C.money_round(v, cur)


def money_fill(s, cur, rng, brand="", city=""):
    s = s.replace("{brand}", brand or "our").replace("{city}", city)
    return re.sub(r"\{money:([\d.]+)\}", lambda m: C.money(round_fee(float(m.group(1)), cur), cur), s)


WD_WORDS = {w: k for k, w in enumerate(C.WEEKDAY)}


def align_weekday(start, texts, season, days):  # noqa: C901
    """if the event copy names a weekday, move the start date to that weekday (inside the season window when possible)"""
    blob = " ".join(t for t in texts if t)
    hits = [k for w, k in WD_WORDS.items() if re.search(r"\b%ss?\b" % w, blob)]
    if not hits and re.search(r"\bweekend\b", blob, re.I):
        hits = [4 if days >= 3 else 5]   # a 'weekend' event starts Friday (3 days) or Saturday
    if len(hits) != 1:
        return start
    k = hits[0]
    a, b = SEASON[season]
    d = start + dt.timedelta(days=(k - start.weekday()) % 7)
    if C.add_days(d, days - 1) > b:
        d = d - dt.timedelta(days=7)
    if d < a:
        d = start + dt.timedelta(days=(k - start.weekday()) % 7)
    return d


# ---------------------------------------------------------------- events
def build_event(e, gid, country, rng, brand, cur, us):
    cty = GE.city(country, rng)
    days = rng.randint(*e["duration_days"])
    start = season_start(e["season"], rng, days)
    if e["season"] in FIXED_DAY and days == 1:
        start = FIXED_DAY[e["season"]]
    sp = {"gid": gid, "e": e, "country": country, "city": cty, "cur": cur, "us": us, "brand": brand}
    if e["commercial"]:
        org_name = brand
    else:
        kinds = ["community centre", "city public health department", "food bank", "university health service", "school",
                 "farmers' market association", "parish/church", "senior citizens' club", "dietitians' network", "chamber of commerce"]
        org_name = GE.org(rng.choice(kinds), country, rng, cty)
    sp["title"] = rng.choice(e["title_patterns"]).replace("{brand}", brand or org_name).replace("{city}", cty["city"].split(",")[0])
    if re.search(r"\bWeek\b", sp["title"]) and days < 5:
        days = 5   # a 'Week' needs at least five days
        start = season_start(e["season"], rng, days)
    cn = cty["city"].split(",")[0]
    sp["subtitle"] = money_fill(e["subtitle"], cur, rng, brand, cn)
    if not (e["season"] in FIXED_DAY and days == 1):
        start = align_weekday(start, [sp["title"], sp["subtitle"]] + [x[2] for x in e["agenda"]] + e["perks"] + e["rules"], e["season"], days)
    sp["organizer"] = org_name
    if country == "US" and e["season"] != "thanksgiving":
        tg = C.nth_weekday(start.year, 11, 3, 4)
        if start <= tg <= C.add_days(start, days - 1):
            start = C.add_days(start, -7)   # nothing but Thanksgiving events runs over Thanksgiving Day
    # Christmas Day / New Year's Day: shops and venues are closed (review round 5: US store opening on 25 Dec)
    closed = {dt.date(2026, 12, 25), dt.date(2027, 1, 1)}
    if {C.add_days(start, k) for k in range(days)} & closed:
        lo, hi = SEASON[e["season"]]
        for step in (7, -7, 14, -14):
            cand = C.add_days(start, step)
            if lo <= cand and C.add_days(cand, days - 1) <= hi and not ({C.add_days(cand, k) for k in range(days)} & closed):
                start = cand
                break
    sp["start"], sp["end"] = start, C.add_days(start, days - 1)
    sp["date2"] = None
    sp["wd_wrong"] = False
    a0, a1 = e["agenda"][0][0], e["agenda"][-1][1]
    hrs = [h for h in e["daily_hours"] if re.match(r"(\d\d:\d\d)\D+(\d\d:\d\d)", h) and re.match(r"(\d\d:\d\d)", h).group(1) <= a0 and re.findall(r"\d\d:\d\d", h)[-1] >= a1]
    hh = rng.choice(hrs) if hrs else "%s–%s" % (a0, a1)   # opening hours must contain the programme
    hs = re.findall(r"\d\d:\d\d", hh)
    sp["hours"] = fmt_range(hs[0], hs[-1], us)
    sp["venue"] = venue_for(e, country, rng, cty, sp["title"], brand)
    sp["hours_label"] = "Opening hours" if days > 1 else "Time"
    sp["addr"] = GE.address(country, rng, cty)
    sp["addr2"] = sp["addr"]
    sp["agenda"] = [list(x) for x in e["agenda"]]
    sp["perks"] = [money_fill(x, cur, rng, brand, cn) for x in e["perks"]]
    sp["rules"] = [money_fill(x, cur, rng, brand, cn) for x in e["rules"]
                   if not (country not in ("UK", "IE", "US", "CA") and re.search(r"alcohol|under-18|over-18", x, re.I))]
    sp["quota"] = e["quota"]
    sp["quota2"] = e["quota"]
    sp["fee"] = round_fee(e["fee_eur"], cur) if e["fee_eur"] else 0
    basis = next((m.group(1) for m in (re.search(r"\bprice is per (\w+)", x, re.I) for x in sp["rules"]) if m), "person")
    sp["fee_text"] = "Free entry" if not sp["fee"] else "Tickets %s per %s" % (C.money(sp["fee"], cur), basis)
    sp["fee_rule"] = None
    sp["speakers"] = ["%s, %s" % (GE.person(rng), r) for r in (e["speaker_roles"] or [])][:2]
    sp["disclaimer"] = e["disclaimer"]
    sp["exag"] = None
    sp["phone"] = GE.phone(country, rng, cty)
    sp["phone2"] = sp["phone"]
    sp["registration"] = e["registration"]
    sp["en_context"] = GE.en_context(country, rng, cty, "community")
    return sp


def dates_text(sp, which=1):
    s, e = sp["start"], sp["end"]
    us = sp["us"]
    if which == 2 and sp["date2"]:
        s, e = sp["date2"]
    if s == e:
        t = C.long_date(s, us=us)
    else:
        t = "%s – %s" % (C.long_date(s, us=us), C.long_date(e, us=us))
    if sp["wd_wrong"] and which == 1:
        wd = C.WEEKDAY[s.weekday()]
        t = t.replace(wd, C.WEEKDAY[(s.weekday() + 1) % 7], 1)
    return t


def ev_date(sp, level, rng, ctx):
    if level == "subtle":
        sp["wd_wrong"] = True
        s = sp["start"]
        return T("event_date_tamper", "weekday", "Header date %s is printed with the weekday %s, but that date is a %s" % (C.long_date(s, us=sp["us"], weekday=False), C.WEEKDAY[(s.weekday() + 1) % 7], C.WEEKDAY[s.weekday()]))
    k = rng.choice([7, 14])
    sp["date2"] = (C.add_days(sp["start"], k), C.add_days(sp["end"], k))
    return T("event_date_tamper", "dates", "Header dates (%s) and the registration box dates (%s) do not match" % (dates_text(sp), dates_text(sp, 2)))


def ev_hidden(sp, level, rng, ctx):
    e = sp["e"]
    hc = money_fill(e["hidden_condition"], sp["cur"], rng, sp["brand"], sp["city"]["city"].split(",")[0])
    if sp["fee"]:
        hc = "The ticket price does not include a compulsory %s materials fee, payable on the day." % C.money(round_fee(12.0, sp["cur"]), sp["cur"])
    sp["rules"].append(hc)
    det = "Hidden paid condition in the small print: \u201c%s\u201d" % hc
    if level == "strong":
        sp["fee_text"] = "100% FREE"
        det += "; header promises \u201c100% FREE\u201d"
    return T("hidden_fee_condition", "rules", det)


def ev_venue(sp, level, rng, ctx):
    if level == "subtle":
        new, n, nn = GE.bump_first_number(sp["addr"], rng.choice([2, 4, 11]))
        if new is None:
            return None
        sp["addr2"] = new
        return T("venue_tamper", "address", "Address in the info box says number %d but the address in the footer says %d" % (n, nn))
    sp["addr2"] = GE.address(sp["country"], rng)
    return T("venue_tamper", "address", "Footer address (%s) is a completely different location from the info-box address (%s)" % (sp["addr2"], sp["addr"]))


def ev_quota(sp, level, rng, ctx):
    q = sp["quota"]
    if re.search(r"no booking|walk in|just drop|just come|drop by", sp.get("registration") or "", re.I):
        # drop-in: the small print lets in more people than the stated venue capacity
        sp["quota2"] = q * 2 if level == "subtle" else q * 4
        return T("quota_contradiction", "quota", "Venue capacity stated as %d in the info box but the small print admits up to %d people" % (q, sp["quota2"]))
    sp["quota2"] = q // 2 if level == "subtle" else max(3, q // 4)
    return T("quota_contradiction", "quota", "Places/gifts stated as %d in the header but %d in the rules" % (q, sp["quota2"]))


def ev_rule(sp, level, rng, ctx):
    if level == "subtle":
        if not sp["rules"]:
            return None
        x = sp["rules"].pop(0)
        return T("promotion_rule_tamper", "rules", "Restricting rule deleted: \u201c%s\u201d" % x)
    sp["rules"].append("The organiser may change the programme, prices or gifts at any time without notice.")
    return T("promotion_rule_tamper", "rules", "Small print added allowing the organiser to change prices/gifts without notice")


def ev_warning(sp, level, rng, ctx):
    if not sp["disclaimer"]:
        return None
    old = sp["disclaimer"]
    sp["disclaimer"] = None
    return T("warning_deletion", "disclaimer", "Health disclaimer deleted: \u201c%s\u201d" % old)


def ev_efficacy(sp, level, rng, ctx):
    x = sp["e"]["exag_line"]
    if not x:
        return None
    sp["exag"] = x
    return T("efficacy_exaggeration", "promise", "Illegal health promise added: \u201c%s\u201d" % x)


def ev_agenda(sp, level, rng, ctx):
    ag = sp["agenda"]
    if len(ag) < 2:
        return None
    k = rng.randrange(1, len(ag))
    prev_end = ag[k - 1][1]
    h, m = map(int, prev_end.split(":"))
    shift = 30 if level == "subtle" else 60
    t = h * 60 + m - shift
    old = ag[k][0]
    ag[k][0] = "%02d:%02d" % (t // 60, t % 60)
    if ag[k][0] >= ag[k][1]:
        ag[k][0] = old
        return None
    return T("agenda_time_conflict", "agenda", "Slot \u201c%s\u201d now starts at %s, before the previous slot ends at %s" % (ag[k][2], ag[k][0], prev_end))


def ev_price(sp, level, rng, ctx):
    if not sp["fee"]:
        if level == "subtle":
            return None
        sp["fee_rule"] = "Admission %s per person, payable at the door." % C.money(round_fee(8.0, sp["cur"]), sp["cur"])
        return T("price_tamper", "fee", "Header says \u201c%s\u201d but the rules charge admission (%s)" % (sp["fee_text"], sp["fee_rule"]))
    f = sp["fee"]
    early = C.money_round(f * 0.8, sp["cur"])
    sp["fee_rule"] = "Early-bird tickets %s (save 40%%) until one week before the event." % C.money(early, sp["cur"])
    return T("price_tamper", "fee", "Early-bird %s is only 20%% below %s, not the stated 40%%" % (C.money(early, sp["cur"]), C.money(f, sp["cur"])))


EVENT_OPS = {"event_date_tamper": ev_date, "hidden_fee_condition": ev_hidden, "venue_tamper": ev_venue, "quota_contradiction": ev_quota,
             "promotion_rule_tamper": ev_rule, "warning_deletion": ev_warning, "efficacy_exaggeration": ev_efficacy,
             "agenda_time_conflict": ev_agenda, "price_tamper": ev_price}


# ---------------------------------------------------------------- PSA
def build_psa(t, gid, country, rng, cur, us, fact_src):
    cty = GE.city(country, rng)
    sp = {"gid": gid, "t": t, "country": country, "city": cty, "us": us, "cur": cur}
    sp["title"] = rng.choice(t["titles"])
    sp["subtitle"] = rng.choice(t["subtitles"]) if t["subtitles"] else None
    if sp["subtitle"] and any(sp["subtitle"] == it for s in t["sections"] for it in s["items"]):
        sp["subtitle"] = None   # avoid printing the same sentence twice (header + bullet)
    sp["organizer"] = GE.org(rng.choice(t["organizer_types"]), country, rng, cty)
    sp["partner"] = GE.org(rng.choice(["community centre", "consumer association", "school", "food bank", "pharmacy"]), country, rng, cty)
    secs = []
    for s in t["sections"]:
        items = list(s["items"])
        if len(items) > 4 and rng.random() < 0.4:
            keep = {nb["text"] for nb in t["numbers"]}
            drop = [i for i in items if i not in keep]
            if drop:
                items.remove(rng.choice(drop))
        secs.append({"heading": s["heading"], "items": items})
    sp["sections"] = secs
    sp["numbers"] = list(t["numbers"])
    sp["key_warning"] = t["key_warning"]
    sp["cta"] = t["cta"]
    sp["phone"] = GE.phone(country, rng, cty)
    sp["phone2"] = sp["phone"]
    sp["emergency"] = {"US": "911", "CA": "911", "UK": "999"}.get(country, "112")
    sp["emergency_label"] = "In an emergency call"
    srcs = [fact_src[nb["fact_id"]] for nb in t["numbers"] if nb["fact_id"] in fact_src and not fact_src[nb["fact_id"]].startswith("(")]
    sp["source"] = "Sources: " + "; ".join(dict.fromkeys(srcs)) if srcs else None
    sp["event"] = None
    yr = SEASON[t["season"]][0].year
    if t["has_event"] and t["event_kinds"]:
        days = 1
        start = season_start(t["season"], rng, days)
        sp["event"] = {"kind": rng.choice(t["event_kinds"]), "date": start, "date2": None, "wd_wrong": False,
                       "time": rng.choice(["10:00–13:00", "14:00–17:00", "09:30–12:30", "16:00–19:00"]),
                       "venue": GE.venue(country, rng), "addr": GE.address(country, rng, cty), "places": rng.choice([30, 40, 50, 60, 80]),
                       "places2": None}
    if sp["event"]:
        yr = sp["event"]["date"].year
        m = re.search(r"\bat (?:the|your|our) ((?:local )?[a-z' -]*?(?:cent(?:er|re)|library|hall|pharmacy|clinic|market))\b", sp["cta"] or "", re.I)
        if m:   # the call to action names the place -> the event box must use the same kind of venue
            sp["event"]["venue"] = "%s, %s" % (m.group(1)[0].upper() + m.group(1)[1:], cty["city"].split(",")[0])
    sp["ref"] = "Ref. %s-%d-%03d" % ("".join(w[0] for w in sp["organizer"].split()[:3] if w[0].isalpha()).upper(), yr, rng.randint(10, 480))
    sp["misinfo"] = None
    sp["en_context"] = GE.en_context(country, rng, cty, "community")
    return sp


def psa_fact(sp, level, rng, ctx):
    nbs = sp["numbers"]
    if not nbs:
        return None
    nb = rng.choice(nbs)
    for s in sp["sections"]:
        s["items"] = [nb["tampered"] if x == nb["text"] else x for x in s["items"]]
    if sp["subtitle"] == nb["text"]:
        sp["subtitle"] = nb["tampered"]
    sp["numbers"] = [x for x in nbs if x is not nb]
    det = "Key fact changed: \u201c%s\u201d -> \u201c%s\u201d" % (nb["text"], nb["tampered"])
    if level == "strong" and sp["numbers"]:
        nb2 = sp["numbers"][0]
        for s in sp["sections"]:
            s["items"] = [nb2["tampered"] if x == nb2["text"] else x for x in s["items"]]
        if sp["subtitle"] == nb2["text"]:
            sp["subtitle"] = nb2["tampered"]
        det += "; \u201c%s\u201d -> \u201c%s\u201d" % (nb2["text"], nb2["tampered"])
    return T("health_fact_tamper", "facts", det)


def psa_misinfo(sp, level, rng, ctx):
    x = sp["t"]["misinfo_subtle"] if level == "subtle" else sp["t"]["misinfo_strong"]
    s = rng.choice(sp["sections"])
    s["items"].insert(rng.randint(1, len(s["items"])), x)
    sp["misinfo"] = x
    return T("misinformation_insertion", "section:" + s["heading"], "False advice inserted into \u201c%s\u201d: \u201c%s\u201d" % (s["heading"], x))


def psa_warning(sp, level, rng, ctx):
    old = sp["key_warning"]
    sp["key_warning"] = None
    return T("warning_deletion", "key_warning", "Key safety warning deleted: \u201c%s\u201d" % old)


def psa_date(sp, level, rng, ctx):
    ev = sp["event"]
    if not ev:
        return None
    if level == "subtle":
        ev["wd_wrong"] = True
        dd = ev["date"]
        return T("event_date_tamper", "weekday", "Event date %s is printed with the weekday %s instead of %s" % (C.long_date(dd, us=sp["us"], weekday=False), C.WEEKDAY[(dd.weekday() + 1) % 7], C.WEEKDAY[dd.weekday()]))
    ev["date2"] = C.add_days(ev["date"], 7)
    return T("event_date_tamper", "dates", "Event box says %s but the footer reminder says %s" % (C.long_date(ev["date"], us=sp["us"]), C.long_date(ev["date2"], us=sp["us"])))


def psa_contact(sp, level, rng, ctx):
    if level == "subtle":
        p = sp["phone"]
        k = max(i for i, ch in enumerate(p) if ch.isdigit())
        sp["phone2"] = p[:k] + str((int(p[k]) + 3) % 10) + p[k + 1:]
        return T("contact_info_tamper", "phone", "Helpline in the footer (%s) differs from the number in the call-to-action box (%s) by one digit" % (sp["phone2"], p))
    old = sp["emergency"]
    sp["emergency"] = {"911": "991", "999": "990", "112": "121"}[old]
    return T("contact_info_tamper", "emergency_number", "Emergency number printed as %s instead of %s" % (sp["emergency"], old))


def psa_quota(sp, level, rng, ctx):
    ev = sp["event"]
    if not ev:
        return None
    ev["places2"] = ev["places"] // 2 if level == "subtle" else ev["places"] * 4
    return T("quota_contradiction", "places", "Event places stated as %d in the event box but %d in the booking line" % (ev["places"], ev["places2"]))


def psa_source(sp, level, rng, ctx):
    if not sp["source"]:
        return None
    old = sp["source"]
    if level == "subtle":
        swap = [("WHO", "UNICEF"), ("NHS", "FDA"), ("FDA", "EFSA"), ("USDA", "EFSA"), ("CDC", "EFSA"), ("Reg (EU)", "Directive (EU)"),
                ("21 CFR", "29 CFR"), ("HRSA", "FDA"), ("EFSA", "FDA"), ("FSA", "FDA")]
        for a, b in swap:
            if a in old:
                sp["source"] = old.replace(a, b, 1)
                return T("source_attribution_tamper", "source", "Source line altered: \u201c%s\u201d attributed to %s instead of %s" % (a, b, a))
        return None
    sp["source"] = "Source: \u201cNatural Health Secrets\u201d blog and reader surveys"
    return T("source_attribution_tamper", "source", "Official source line replaced by an unreliable blog: \u201c%s\u201d (was \u201c%s\u201d)" % (sp["source"], old))


PSA_OPS = {"health_fact_tamper": psa_fact, "misinformation_insertion": psa_misinfo, "warning_deletion": psa_warning,
           "event_date_tamper": psa_date, "contact_info_tamper": psa_contact, "quota_contradiction": psa_quota,
           "source_attribution_tamper": psa_source}
