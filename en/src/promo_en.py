"""Promotions for commercial ads (prices, dates, rules) + tamper ops."""
import common_en as C


def T(t, f, d):
    return {"type": t, "field": f, "detail": d}


PTYPES = {"UK": ["was_now", "save_pct", "multi", "bogof", "three_for_two", "member", "flash"],
          "IE": ["was_now", "save_pct", "multi", "bogof", "member", "flash"],
          "US": ["sale_reg", "save_pct", "multi", "b2g1", "member", "flash", "coupon"],
          "EU": ["save_pct", "second_half", "three_for_two", "member", "flash", "was_now"]}


def make(rng, sp, region, cur, start, days, us_dates):
    """price + period + mechanism. sp = food spec (or supp spec) with pack price_eur."""
    lo, hi = sp["price_eur"]
    orig = C.eur_to(rng.uniform(lo, hi), cur, rng)
    pt = rng.choice(PTYPES[region])
    p = {"cur": cur, "type": pt, "orig": orig, "start": start, "end": C.add_days(start, days - 1), "us": us_dates,
         "limit": rng.choice([2, 3, 4, 6]), "quota": None, "rules_extra": [], "headline_override": None,
         "hidden": None, "rule_deleted": None, "end_rule": None, "weekday_wrong": False, "label_pct": None}
    if pt in ("was_now", "sale_reg", "save_pct", "member", "flash", "coupon"):
        pct = rng.choice([20, 25, 30, 33, 40, 50]) if pt != "member" else rng.choice([10, 15, 20, 25])
        p["pct"] = pct
        p["sale"] = C.money_round(orig * (100 - pct) / 100.0, cur)
        if pt == "flash":
            p["quota"] = rng.choice([100, 150, 200, 300, 500])
    elif pt == "multi":
        k = rng.choice([2, 3])
        p["k"] = k
        p["multi_price"] = C.money_round(orig * k * rng.uniform(0.7, 0.85), cur)
    elif pt in ("bogof", "b2g1", "three_for_two", "second_half"):
        p["pct"] = {"bogof": 50, "b2g1": 33, "three_for_two": 33, "second_half": 25}[pt]
    return p


def m(p, x):
    return C.money(x, p["cur"])


def period_text(p, which="main"):
    end = p["end_rule"] if (which == "rule" and p["end_rule"]) else p["end"]
    s, e = p["start"], end
    if p["weekday_wrong"] and which == "main":
        wd = (e.weekday() + 1) % 7
        es = C.short_date(e, us=p["us"]).replace(C.WD3[e.weekday()], C.WD3[wd])
    else:
        es = C.short_date(e, us=p["us"])
    return "%s – %s %d" % (C.short_date(s, us=p["us"]), es, e.year)


def headline(p, unit):
    if p["headline_override"]:
        return [p["headline_override"]]
    t = p["type"]
    if t == "was_now":
        return ["Was %s" % m(p, p["orig"]), "Now %s" % m(p, p["sale"])]
    if t == "sale_reg":
        return ["Sale %s" % m(p, p["sale"]), "Reg. %s" % m(p, p["orig"])]
    if t == "save_pct":
        return ["Save %d%%" % (p["label_pct"] or p["pct"]), "Now %s" % m(p, p["sale"]), "Was %s" % m(p, p["orig"])]
    if t == "member":
        return ["Member price %s" % m(p, p["sale"]), "Non-member price %s" % m(p, p["orig"])]
    if t == "flash":
        return ["Flash deal %s" % m(p, p["sale"]), "Usual price %s" % m(p, p["orig"]), "Only %d available" % p["quota"]]
    if t == "coupon":
        return ["%d%% off with digital coupon" % (p["label_pct"] or p["pct"]), "Final price %s" % m(p, p["sale"]), "Reg. %s" % m(p, p["orig"])]
    if t == "multi":
        return ["Any %d for %s" % (p["k"], m(p, p["multi_price"])), "Single %s %s" % (unit, m(p, p["orig"]))]
    if t == "bogof":
        return ["Buy one get one free", "%s each" % m(p, p["orig"])]
    if t == "b2g1":
        return ["Buy 2 get 1 free", "%s each" % m(p, p["orig"])]
    if t == "three_for_two":
        return ["3 for 2", "%s each" % m(p, p["orig"])]
    return ["2nd item half price", "%s each" % m(p, p["orig"])]


def rules(p, product):
    t = p["type"]
    L = ["Offer valid %s while stocks last." % period_text(p, "rule")]
    if t in ("was_now", "sale_reg", "save_pct", "flash", "coupon", "member"):
        L.append("%s at %s, limit %d per customer." % (product, m(p, p.get("rule_sale") or p["sale"]), p["limit"]))
    if t == "member":
        L.append("Member price applies when you scan your free membership card or app at the till.")
    if t == "coupon":
        L.append("Clip the digital coupon in the app before checkout; one coupon per transaction.")
    if t == "flash" and p["quota"]:
        L.append("Flash price limited to the first %d units sold." % p["quota"])
    if t == "multi":
        L.append("Mix and match any %d; single items charged at %s." % (p["k"], m(p, p["orig"])))
    if t in ("bogof", "b2g1", "three_for_two"):
        L.append("Cheapest item free; mix and match across the range.")
    if t == "second_half":
        L.append("Discount applied to the cheaper item at the till.")
    if p.get("drop_price_rule"):
        L = [x for x in L if ", limit " not in x]
    L += p["rules_extra"]
    if p["rule_deleted"]:
        L = [x for x in L if x != p["rule_deleted"]]
    return L


# ---------------------------------------------------------------- ops
def op_price(p, sp, level, rng, ctx):
    t = p["type"]
    if level == "subtle":
        if t in ("save_pct", "coupon"):
            real = 100 - round(100 * p["sale"] / p["orig"])
            p["label_pct"] = p["pct"] + rng.choice([10, 15])
            return T("price_tamper", "discount_math", "Badge says \u201c%d%% off\u201d but %s from %s is only about %d%% off" % (p["label_pct"], m(p, p["sale"]), m(p, p["orig"]), real))
        if t in ("was_now", "sale_reg", "member", "flash"):
            p["rule_sale"] = C.money_round(p["sale"] * rng.choice([1.08, 1.12, 1.15]), p["cur"])
            return T("price_tamper", "headline_vs_rules", "Headline price %s but the rules say the item is charged at %s" % (m(p, p["sale"]), m(p, p["rule_sale"])))
        if t == "multi":
            old = p["multi_price"]
            p["multi_price"] = C.money_round(p["orig"] * p["k"] * rng.uniform(1.02, 1.08), p["cur"])
            return T("price_tamper", "multi_buy", "\u201cAny %d for %s\u201d costs more than buying %d single items at %s" % (p["k"], m(p, p["multi_price"]), p["k"], m(p, p["orig"])))
        return None
    low = C.money_round(p["orig"] * 0.2, p["cur"])
    p["headline_override"] = "From %s" % m(p, low)
    p["drop_price_rule"] = True
    p["rules_extra"].append("%s price applies only to the 3rd item when two items are bought at the full price of %s." % (m(p, low), m(p, p["orig"])))
    return T("price_tamper", "headline_vs_rules", "Headline \u201cFrom %s\u201d; the small print says it applies only to a third item after buying two at the full %s" % (m(p, low), m(p, p["orig"])))


def op_promo_date(p, sp, level, rng, ctx):
    if level == "subtle":
        if rng.random() < 0.5:
            p["weekday_wrong"] = True
            e = p["end"]
            return T("promotion_date_tamper", "weekday", "End date %s is labelled with the wrong weekday (%s instead of %s)" % (C.short_date(e, us=p["us"], weekday=False), C.WD3[(e.weekday() + 1) % 7], C.WD3[e.weekday()]))
        p["end_rule"] = C.add_days(p["end"], rng.choice([2, 3, 7]))
        return T("promotion_date_tamper", "period", "Banner ends %s but the small-print rules end %s" % (C.short_date(p["end"], us=p["us"]), C.short_date(p["end_rule"], us=p["us"])))
    p["end_rule"] = C.add_days(p["end"], 30)
    p["headline_extra"] = "%d days only!" % ((p["end"] - p["start"]).days + 1)
    return T("promotion_date_tamper", "period", "Headline says \u201c%s\u201d (%s) but the rules run the offer until %s" % (p["headline_extra"], period_text(p), C.short_date(p["end_rule"], us=p["us"])))


def op_promo_rule(p, sp, level, rng, ctx):
    if level == "subtle":
        lim = [x for x in rules(p, sp["core"]) if "limit" in x.lower() or "one per" in x.lower() or "first" in x.lower()]
        if not lim:
            return None
        p["rule_deleted"] = lim[0]
        return T("promotion_rule_tamper", "rules", "Restricting rule deleted: \u201c%s\u201d" % lim[0])
    p["rules_extra"].append("Final price is determined at the till; the store may change or withdraw this offer at any time without notice.")
    return T("promotion_rule_tamper", "rules", "Small print added that lets the store change the advertised price at the till without notice, contradicting the headline price")


def op_hidden(p, sp, level, rng, ctx):
    fee = C.money_round(C.eur_to(rng.choice([4.0, 6.0, 9.0]), p["cur"]), p["cur"])
    if level == "subtle":
        p["rules_extra"].append("Free gift requires a paid Plus membership (%s per month)." % m(p, fee))
        p["gift"] = True
        return T("hidden_fee_condition", "gift", "Free gift is conditional on a paid membership of %s/month mentioned only in the small print" % m(p, fee))
    p["gift"] = True
    p["rules_extra"].append("Free gift and offer price available only to Plus members (annual fee %s, billed at the till)." % m(p, fee * 10))
    return T("hidden_fee_condition", "offer", "Headline offer and \u201cFREE gift\u201d are only for members paying an annual fee of %s, disclosed only in the small print" % m(p, fee * 10))


def op_quota(p, sp, level, rng, ctx):
    q = p["quota"] or rng.choice([100, 200, 300])
    p["quota"] = q
    p["gift"] = True
    q2 = q // 2 if level == "subtle" else q // 5
    p["rules_extra"].append("Free gift limited to the first %d customers." % q2)
    p["gift_quota"] = q
    return T("quota_contradiction", "quota", "Banner promises a free gift for the first %d customers but the rules limit it to the first %d" % (q, q2))


PROMO_OPS = {"price_tamper": op_price, "promotion_date_tamper": op_promo_date, "promotion_rule_tamper": op_promo_rule,
             "hidden_fee_condition": op_hidden, "quota_contradiction": op_quota}
