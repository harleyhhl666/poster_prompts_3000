"""Promotion model + promo tamper operators (used by commercial ads)."""
from common import add_days, md_cn, weekday_cn, fmt_date, money, money_short


def _t(type_, field, detail):
    return {"type": type_, "field": field, "detail": detail}


FESTIVALS = [  # (key, name, start, days, headline words)
    ("guoqing", "国庆", (2026, 10, 1), 7, ["国庆好物节", "金秋国庆 欢乐购"]),
    ("shuang11", "双11", (2026, 11, 1), 11, ["双11狂欢购", "11.11 囤货节"]),
    ("shuang12", "双12", (2026, 12, 8), 5, ["双12年终盛典", "12.12 暖冬好价"]),
    ("yuandan", "元旦", (2026, 12, 30), 4, ["元旦跨年购", "新年焕新 元旦特惠"]),
    ("nianhuo", "年货节", (2027, 1, 15), 21, ["年货节 置办好年货", "新春年货大集"]),
    ("zhongqiu", "中秋", (2026, 9, 12), 14, ["中秋团圆礼", "月满中秋 好礼相伴"]),
    ("chunji", "开学季", (2027, 2, 22), 10, ["开学季 能量补给", "元气开学季"]),
    ("weekly", "周末", None, 2, ["周末特惠", "周末惊喜价"]),
    ("anniv", "店庆", None, 5, ["店庆感恩回馈", "周年庆 限时特惠"]),
    ("newlaunch", "新品", None, 14, ["新品上市 尝鲜价", "新品首发"]),
    ("member", "会员日", None, 1, ["会员日 专享价", "每周三会员日"]),  # start date forced to a Wednesday below
    ("flash", "秒杀", None, 1, ["限时秒杀", "整点秒杀"]),
]


def make_promo(rng, spec, fest, ptype, date_rng_start=None):
    import datetime as dt
    key, fname, st, days, heads = fest
    if st:
        start = dt.date(*st)
    else:
        start = date_rng_start or dt.date(2026, 10, 1) + dt.timedelta(days=rng.randint(0, 150))
        if key == "weekly":
            while start.weekday() != 5:
                start += dt.timedelta(days=1)
        if key == "member":
            while start.weekday() != 2:
                start += dt.timedelta(days=1)
    end = add_days(start, days - 1)
    orig = spec["price_orig"]
    p = {"fest_key": key, "fest_name": fname, "headline": rng.choice(heads), "start": start, "end": end,
         "type": ptype, "orig": orig, "limit": rng.choice([2, 3, 5, 6]), "time_of_day": None,
         "rules": [], "rules_extra": [], "gift": None, "quota": None, "quota_shown2": None,
         "end_shown2": None, "start_shown2": None, "headline_price_text": None, "settle_note": None,
         "discount_text": None, "weekday_shown": None, "fine_print_override": None, "hidden_condition": None,
         "rule_deleted": None, "headline_days": None}
    if key == "flash":
        p["time_of_day"] = rng.choice(["10:00—12:00", "20:00—22:00", "12:00—14:00"])
    if key == "shuang11" and rng.random() < 0.5:
        p["start"] = end
        p["time_of_day"] = "00:00—23:59"
    if ptype == "直降":
        act = round(orig * rng.choice([0.7, 0.75, 0.8, 0.85]), 1)
        act = float(f"{int(act)}.9") if act >= 10 else round(act, 1)
        if act >= orig:
            act = round(orig - 1, 1)
        p["act"] = act
        p["discount_text"] = f"直降{money_short(orig - act)}元"
    elif ptype == "折扣":
        z = rng.choice([5, 6, 7, 8, 8.5, 8.8])
        p["zhe"] = z
        p["act"] = round(orig * z / 10, 2)
        p["discount_text"] = f"限时{money_short(z)}折"
    elif ptype == "第二件半价":
        p["act"] = orig
        p["second"] = round(orig / 2, 2)
        p["discount_text"] = "第二件半价"
    elif ptype == "买二送一":
        p["act"] = orig
        p["discount_text"] = "买二送一"
    elif ptype == "满减":
        th = rng.choice([59, 69, 99, 129, 199])
        cut = {59: 10, 69: 15, 99: 20, 129: 30, 199: 50}[th]
        p["act"] = orig
        p["threshold"], p["cut"] = th, cut
        p["discount_text"] = f"满{th}减{cut}"
    elif ptype == "会员价":
        act = round(orig * rng.choice([0.8, 0.85, 0.9]), 1)
        p["act"] = orig
        p["member"] = float(f"{int(act)}.9") if act >= 10 else act
        p["discount_text"] = f"会员价¥{money(p['member'])}"
    elif ptype == "组合价":
        n = rng.choice([2, 3])
        tot = round(orig * n * rng.choice([0.75, 0.8]), 0) - 0.1
        p["act"] = orig
        p["combo_n"], p["combo"] = n, round(tot, 1)
        p["discount_text"] = f"{n}件组合价¥{money(p['combo'])}"
    elif ptype == "秒杀":
        act = round(orig * rng.choice([0.5, 0.55, 0.6]), 1)
        p["act"] = float(f"{int(act)}.9") if act >= 10 else act
        p["discount_text"] = f"秒杀价¥{money(p['act'])}"
        p["quota"] = rng.choice([200, 300, 500, 1000])
    if ptype in ("买二送一",) or rng.random() < 0.35:
        p["gift"] = rng.choice(["品牌定制帆布袋1个", "同款小包装试吃装1份", "保温杯1个（限量）", "环保购物袋1个", "定制冰箱贴1枚"])
        p["gift_threshold"] = rng.choice([59, 88, 99, 128])
        if p["quota"] is None:
            p["quota"] = rng.choice([100, 200, 300, 500])
    return p


def promo_date_text(p, which="headline"):
    s = p["start_shown2"] if (which == "rules" and p["start_shown2"]) else p["start"]
    e = p["end_shown2"] if (which == "rules" and p["end_shown2"]) else p["end"]
    if s == e:
        wd = p["weekday_shown"] or weekday_cn(s)
        t = f"{s.year}年{md_cn(s)}（{wd}）"
        if p["time_of_day"]:
            t += f" {p['time_of_day']}"
        return t
    if which == "headline":
        return f"{s.year}.{s.month}.{s.day}—{e.year}.{e.month}.{e.day}" if s.year != e.year else f"{s.year}.{s.month}.{s.day}—{e.month}.{e.day}"
    t = f"{s.year}年{md_cn(s)}至{e.year}年{md_cn(e)}" if s.year != e.year else f"{s.year}年{md_cn(s)}至{md_cn(e)}"
    if p["time_of_day"]:
        t += f" 每日{p['time_of_day']}"
    return t


def price_block(p):
    """Returns list of lines for the big price area."""
    o = f"原价¥{money(p['orig'])}"
    t = p["type"]
    if p.get("headline_price_text"):
        return [p["headline_price_text"], o]
    if t in ("直降", "折扣"):
        return [f"活动价 ¥{money(p['act'])}", o, p["discount_text"]]
    if t == "秒杀":
        return [f"秒杀价 ¥{money(p['act'])}", o]
    if t == "第二件半价":
        return [f"单件¥{money(p['orig'])}", f"第二件半价 仅¥{money(p['second'])}"]
    if t == "买二送一":
        return [f"单件¥{money(p['orig'])}", "买二送一"]
    if t == "满减":
        return [f"¥{money(p['orig'])}", p["discount_text"]]
    if t == "会员价":
        return [f"会员价 ¥{money(p['member'])}", f"非会员价¥{money(p['orig'])}"]
    if t == "组合价":
        return [f"{p['combo_n']}件组合价 ¥{money(p['combo'])}", f"单件原价¥{money(p['orig'])}"]
    return [o]


def rules_lines(p, spec):
    r = [f"活动时间：{promo_date_text(p, 'rules')}"]
    t = p["type"]
    if p.get("fine_print_override"):
        r.append(p["fine_print_override"])
    elif t in ("直降", "折扣"):
        r.append(f"活动期间{spec['name_core']}（{spec['net_text']}）按活动价¥{money(p['act'])}结算，每人每日限购{p['limit']}件")
    elif t == "秒杀":
        r.append(f"秒杀商品限量{p['quota_shown2'] or p['quota']}件，每个账号限购{p['limit']}件，售完即止")
    elif t == "第二件半价":
        r.append(f"购买同款商品2件，第二件按半价¥{money(p['second'])}结算，每人限购{p['limit']*2}件")
    elif t == "买二送一":
        r.append(f"购买2件同款商品赠送同款1件，赠品随单发出，每人限参与{p['limit']}次")
    elif t == "满减":
        r.append(f"活动商品单笔订单满{p['threshold']}元立减{p['cut']}元，不与其他优惠同享")
    elif t == "会员价":
        r.append("会员价需出示会员码或登录会员账号，每位会员限购" + str(p["limit"]) + "件")
    elif t == "组合价":
        r.append(f"{p['combo_n']}件组合须为同款商品，组合价¥{money(p['combo'])}，单独购买按原价¥{money(p['orig'])}结算")
    if p.get("settle_note"):
        r.append(p["settle_note"])
    if p["gift"]:
        q = p["quota_shown2"] or p["quota"]
        r.append(f"单笔消费满{p['gift_threshold']}元赠{p['gift'].replace('（限量）', '')}，限前{q}名，送完即止")
    if p.get("hidden_condition"):
        r.append(p["hidden_condition"])
    if not p.get("rule_deleted"):
        r.append("活动商品数量有限，售完即止；特价商品不与会员积分翻倍同享")
    r.extend(p["rules_extra"])
    return r


# ---------------- promo tamper operators
def op_price(p, spec, level, rng):
    t = p["type"]
    if level == "subtle":
        if t in ("直降", "秒杀"):
            new = round(p["act"] + rng.choice([3, 5, 2]), 1)
            p["settle_note"] = f"会员积分按实付金额累计，活动商品收银结算单价¥{money(new)}"
            return _t("price_tamper", "promo_price", f"大字活动价¥{money(p['act'])}，小字规则中结算价却写¥{money(new)}")
        if t == "折扣":
            wrong = round(p["orig"] * (p["zhe"] + 1) / 10, 2)
            p["act"] = wrong
            return _t("price_tamper", "discount_math",
                      f"标示「限时{money_short(p['zhe'])}折」，但活动价¥{money(wrong)}实际约为{money_short(round(wrong / p['orig'] * 10, 1))}折，折扣与价格不一致")
        if t == "第二件半价":
            p["second"] = round(p["orig"] * 0.6, 2)
            return _t("price_tamper", "second_item_price",
                      f"「第二件半价」但第二件价格写作¥{money(p['second'])}，不是单价¥{money(p['orig'])}的一半")
        if t == "会员价":
            p["member"] = round(p["member"] + 4, 1)
            return _t("price_tamper", "member_price", f"会员价被上调为¥{money(p['member'])}，与宣传区“会员立省”金额不符")
        if t == "组合价":
            p["combo"] = round(p["orig"] * p["combo_n"] + 0.5, 1)
            return _t("price_tamper", "combo_price", f"组合价¥{money(p['combo'])}反而高于单件原价×件数，组合优惠名不副实")
        if t == "满减":
            p["settle_note"] = f"满减门槛以实付金额满{p['threshold'] + 30}元计算"
            return _t("price_tamper", "threshold", f"大字写满{p['threshold']}减{p['cut']}，小字门槛写成满{p['threshold']+30}元")
        if t == "买二送一":
            p["fine_print_override"] = "购买3件同款商品赠送同款1件，赠品随单发出"
            return _t("price_tamper", "bundle_rule", "大字「买二送一」，小字规则写成买3件才赠1件")
    # strong
    ch = rng.random()
    if t in ("第二件半价", "买二送一") or ch < 0.33:
        p["headline_price_text"] = "第二件0元"
        p["fine_print_override"] = f"购买同款商品2件，第二件按半价¥{money(round(p['orig']/2,2))}结算"
        return _t("price_tamper", "headline_vs_rules", "主标题写「第二件0元」，规则小字实际为第二件半价")
    if ch < 0.66:
        low = round(p["act"] * 0.35, 1)
        low = max(0.9, float(f"{int(low)}.9") if low >= 1 else 0.9)
        if low >= p["orig"] * 0.6:
            low = round(p["orig"] * 0.3, 1)
        p["headline_price_text"] = f"¥{money(low)}起"
        p["settle_note"] = f"¥{money(low)}为第3件加购价，需同时购买2件原价商品，单件实付最低¥{money(p['orig'])}"
        return _t("price_tamper", "headline_vs_rules", f"大字「¥{money(low)}起」，小字写明需先购2件原价商品，单件实付最低¥{money(p['orig'])}")
    inflated = float(f"{int(p['orig'] * rng.choice([2.2, 2.5, 3.0]))}.9")
    old = p["orig"]
    p["orig"] = inflated
    if t in ("直降",):
        p["discount_text"] = f"直降{money_short(inflated - p['act'])}元"
    return _t("price_tamper", "original_price", f"原价由¥{money(old)}虚高为¥{money(inflated)}，制造大幅降价假象")


def op_promo_date(p, spec, level, rng):
    if level == "subtle":
        if p["start"] != p["end"] and rng.random() < 0.6:
            ne = add_days(p["end"], rng.choice([3, 5, 7]))
            p["end_shown2"] = ne
            return _t("promotion_date_tamper", "promo_end_date",
                      f"主视觉活动日期至{md_cn(p['end'])}，规则小字却写至{md_cn(ne)}，两处截止日期不一致")
        s = p["start"]
        wrong = weekday_cn(add_days(s, 1))
        if s == p["end"]:
            p["weekday_shown"] = wrong
            return _t("promotion_date_tamper", "promo_weekday", f"活动日期{md_cn(s)}实际为{weekday_cn(s)}，画面标注为（{wrong}）")
        ns = add_days(s, -2)
        p["start_shown2"] = ns
        return _t("promotion_date_tamper", "promo_start_date", f"规则小字中活动开始日期写成{md_cn(ns)}，与主视觉{md_cn(s)}不一致")
    ne = add_days(p["end"], rng.choice([30, 31, 45]))
    p["end_shown2"] = ne
    p["headline_days"] = "仅限3天" if (p["end"] - p["start"]).days >= 2 else "今日最后1天"
    p["rules_extra"].append(f"活动如有延期，以本店通知为准")
    return _t("promotion_date_tamper", "promo_period",
              f"主视觉写「{p['headline_days']}」，但同屏标注的活动日期为{md_cn(p['start'])}—{md_cn(p['end'])}（共{(p['end'] - p['start']).days + 1}天），"
              f"规则小字活动期限又延长至{ne.year}年{md_cn(ne)}，三处期限互相矛盾")


def op_promo_rule(p, spec, level, rng):
    if level == "subtle":
        p["rule_deleted"] = True
        return _t("promotion_rule_tamper", "promo_rule", "删除了“活动商品数量有限、特价商品不与积分翻倍同享”的限制性规则，其余规则保留")
    p["rule_deleted"] = True
    p["rules_extra"].append("本活动最终解释权归本店所有，实际优惠以收银台结算为准，恕不另行通知")
    return _t("promotion_rule_tamper", "promo_rule", "删除限制规则，改为“实际优惠以收银台结算为准，恕不另行通知”的免责式条款，活动价格不再确定")


def op_hidden(p, spec, level, rng):
    if not p["gift"]:
        return None
    if level == "subtle":
        p["hidden_condition"] = f"赠品需另付包装费¥{rng.choice([5, 9, 12])}.90"
        return _t("hidden_fee_condition", "gift_condition", "赠品在规则小字中附加了额外付费的包装费条件")
    p["headline_gift_free"] = True
    p["hidden_condition"] = f"赠品需办理¥{rng.choice([99, 199, 299])}年卡会员后领取"
    return _t("hidden_fee_condition", "gift_condition", "主视觉写“免费送”，规则小字要求先办理付费年卡会员才可领取")


def op_quota(p, spec, level, rng):
    if not p["quota"]:
        return None
    q = p["quota"]
    nq = q + rng.choice([100, 200]) if level == "subtle" else q * 5
    p["quota_shown2"] = nq
    return _t("quota_contradiction", "quota", f"主视觉写限量{q}份/名，规则小字写前{nq}名/件，名额前后矛盾")


PROMO_OPS = {"price_tamper": op_price, "promotion_date_tamper": op_promo_date, "promotion_rule_tamper": op_promo_rule,
             "hidden_fee_condition": op_hidden, "quota_contradiction": op_quota}
