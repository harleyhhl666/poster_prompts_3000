"""Shared helpers: deterministic RNG, dates, nutrition math (GB 28050-2011 based), formatting."""
import datetime as dt
import hashlib
import random
import calendar

WEEK = "一二三四五六日"


def rng_for(*keys):
    seed = int(hashlib.md5("|".join(map(str, keys)).encode("utf-8")).hexdigest()[:12], 16)
    return random.Random(seed)


def D(y, m, d):
    return dt.date(y, m, d)


def add_days(d, n):
    return d + dt.timedelta(days=n)


def add_months(d, m):
    y = d.year + (d.month - 1 + m) // 12
    mo = (d.month - 1 + m) % 12 + 1
    day = min(d.day, calendar.monthrange(y, mo)[1])
    return dt.date(y, mo, day)


def expiry_of(prod, val, unit):
    """Dataset convention: 保质期至 = production date + shelf life - 1 day."""
    if unit == "月":
        return add_days(add_months(prod, val), -1)
    if unit == "天":
        return add_days(prod, val - 1)
    if unit == "小时":
        return prod  # same-day items; handled separately
    raise ValueError(unit)


def fmt_date(d, style):
    if style == "cn0":
        return f"{d.year}年{d.month:02d}月{d.day:02d}日"
    if style == "cn":
        return f"{d.year}年{d.month}月{d.day}日"
    if style == "iso":
        return d.strftime("%Y-%m-%d")
    if style == "dot":
        return d.strftime("%Y.%m.%d")
    if style == "slash":
        return d.strftime("%Y/%m/%d")
    raise ValueError(style)


def md_cn(d):
    return f"{d.month}月{d.day}日"


def weekday_cn(d):
    return "周" + WEEK[d.weekday()]


def shelf_str(val, unit):
    return f"{val}个月" if unit == "月" else f"{val}{unit}"


# ---------------- nutrition (GB 28050-2011 Annex A NRV; rounding & "0" limits) ----------------
NRV = {
    "energy": 8400, "protein": 60, "fat": 60, "sat": 20, "carb": 300, "fiber": 25,
    "sodium": 2000, "calcium": 800, "vitc": 100, "iron": 15, "potassium": 2000,
    "vitd": 5, "zinc": 15, "vita": 800,
}
NUT_NAME = {
    "energy": "能量", "protein": "蛋白质", "fat": "脂肪", "sat": "—饱和脂肪", "trans": "—反式脂肪",
    "carb": "碳水化合物", "sugar": "—糖", "lactose": "—乳糖", "fiber": "膳食纤维", "sodium": "钠",
    "calcium": "钙", "vitc": "维生素C", "iron": "铁", "potassium": "钾", "vitd": "维生素D", "zinc": "锌",
    "vita": "维生素A",
}
UNIT_SYM = {"energy": "kJ", "sodium": "mg", "calcium": "mg", "vitc": "mg", "iron": "mg", "potassium": "mg",
            "zinc": "mg", "vitd": "μg", "vita": "μgRE"}
UNIT_CN = {"kJ": "千焦", "g": "克", "mg": "毫克", "μg": "微克", "μgRE": "微克视黄醇当量"}
ZERO = {"energy": 17, "protein": 0.5, "fat": 0.5, "sat": 0.1, "trans": 0.3, "carb": 0.5, "sugar": 0.5,
        "lactose": 0.5, "fiber": 0.5, "sodium": 5, "calcium": 8, "vitc": 2.0, "iron": 0.3, "potassium": 20,
        "vitd": 0.1, "zinc": 0.1, "vita": 8}
ORDER = ["energy", "protein", "fat", "sat", "trans", "carb", "sugar", "lactose", "fiber", "sodium",
         "calcium", "potassium", "vitc", "vitd", "vita", "iron", "zinc"]
INT_KEYS = {"energy", "sodium", "calcium", "potassium", "vita"}


def unit_of(k):
    return UNIT_SYM.get(k, "g")


def round_val(k, v):
    if v <= ZERO.get(k, 0):
        return 0
    if k in INT_KEYS:
        return int(round(v))
    return round(v, 1)


def energy_kj(p, f, c, fiber=0.0, polyol=0.0):
    return 17 * p + 37 * f + 17 * max(c - polyol, 0) + 8 * fiber


def nrv_pct(k, shown):
    """GB 28050 A.2: NRV% rounded to integer (half-up, not Python's banker's rounding)."""
    if k not in NRV:
        return None
    import math
    return int(math.floor(round(shown / NRV[k] * 100, 6) + 0.5))


def fmt_num(k, v):
    if v == 0:
        return "0"
    if k in INT_KEYS:
        return str(int(v))
    return f"{v:.1f}"


def build_nutrition(base, keys, rng, jitter=0.08, polyol=0.0, scale=1.0, solid=False):
    """base: per-100 values. returns dict k->shown value (per basis) with energy computed consistently."""
    vals = {}
    for k in keys:
        if k == "energy":
            continue
        b = base.get(k, 0.0)
        v = b * (1 + rng.uniform(-jitter, jitter)) if b else 0.0
        vals[k] = v
    if "sugar" in vals and "carb" in vals and vals["sugar"] > vals["carb"]:
        vals["sugar"] = vals["carb"] * 0.92
    if "sat" in vals and vals["sat"] > vals.get("fat", 0):
        vals["sat"] = vals["fat"] * 0.6
    if "lactose" in vals and vals["lactose"] > vals.get("carb", 0):
        vals["lactose"] = vals["carb"] * 0.9
    macro = sum(vals.get(k, 0) for k in ("protein", "fat", "carb", "fiber"))
    if solid and macro > 99:
        f = 99 / macro
        for k in ("protein", "fat", "carb", "fiber", "sugar", "sat", "lactose"):
            if k in vals:
                vals[k] *= f
    shown = {k: (0 if v <= ZERO.get(k, 0) else round_val(k, v * scale) or (int(1) if k in INT_KEYS else 0.1))
             for k, v in vals.items()}
    e100 = energy_kj(vals.get("protein", 0), vals.get("fat", 0), vals.get("carb", 0), vals.get("fiber", 0), polyol)
    e = energy_kj(shown.get("protein", 0), shown.get("fat", 0), shown.get("carb", 0), shown.get("fiber", 0),
                  polyol * scale)
    shown["energy"] = 0 if e100 <= ZERO["energy"] else max(1, int(round(e)))
    return shown


def nutrition_rows(shown, keys, unit_style="sym"):
    rows = []
    for k in ORDER:
        if k not in keys:
            continue
        v = shown[k]
        u = unit_of(k)
        u_disp = u if unit_style == "sym" else UNIT_CN[u]
        pct = nrv_pct(k, v)
        rows.append({"key": k, "name": NUT_NAME[k], "value": v, "unit": u_disp,
                     "nrv": (f"{pct}%" if pct is not None else "—")})
    return rows


def money(x):
    return f"{x:.2f}"


def money_short(x):
    s = f"{x:.2f}"
    return s[:-3] if s.endswith(".00") else (s[:-1] if s.endswith("0") else s)
