"""Shared helpers for the English engine: seeded RNG, dates, money, units, codes, rounding."""
import calendar
import re
import datetime as dt
import hashlib
import math
import random

WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WD3 = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
       "December"]
MON3 = [m[:3].upper() for m in MON]


def rng_for(*keys):
    h = hashlib.md5("|".join(str(k) for k in keys).encode("utf-8")).hexdigest()
    return random.Random(int(h[:16], 16))


def add_days(d, n):
    return d + dt.timedelta(days=n)


def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    y += d.year
    mo += 1
    return dt.date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))


def expiry_of(prod, val, unit):
    """dataset convention (same as zh part): best-before = production + shelf life - 1 day"""
    end = add_months(prod, val) if unit == "months" else add_days(prod, val)
    return add_days(end, -1)


def shelf_str(val, unit):
    u = unit if val != 1 else unit[:-1]
    return "%d %s" % (val, u)


# date styles. eu: day-first; us: month-first
DATE_STYLES = {"eu": ["dd.mm.yyyy", "dd/mm/yyyy", "dd MON yyyy"], "us": ["mm/dd/yyyy", "MON dd yyyy", "mm/dd/yy"]}


def fmt_date(d, style):
    if style == "dd.mm.yyyy":
        return d.strftime("%d.%m.%Y")
    if style == "dd/mm/yyyy":
        return d.strftime("%d/%m/%Y")
    if style == "dd MON yyyy":
        return "%02d %s %d" % (d.day, MON3[d.month - 1], d.year)
    if style == "mm/dd/yyyy":
        return d.strftime("%m/%d/%Y")
    if style == "MON dd yyyy":
        return "%s %02d %d" % (MON3[d.month - 1], d.day, d.year)
    if style == "mm/dd/yy":
        return d.strftime("%m/%d/%y")
    raise ValueError(style)


def long_date(d, us=False, weekday=True):
    """'Saturday 14 November 2026' (eu) / 'Saturday, November 14, 2026' (us)"""
    if us:
        s = "%s %d, %d" % (MON[d.month - 1], d.day, d.year)
        return (WEEKDAY[d.weekday()] + ", " + s) if weekday else s
    s = "%d %s %d" % (d.day, MON[d.month - 1], d.year)
    return (WEEKDAY[d.weekday()] + " " + s) if weekday else s


def short_date(d, us=False, weekday=True):
    """'Sat 14 Nov' / 'Sat, Nov 14'"""
    if us:
        s = "%s %d" % (MON[d.month - 1][:3], d.day)
        return (WD3[d.weekday()] + ", " + s) if weekday else s
    s = "%d %s" % (d.day, MON[d.month - 1][:3])
    return (WD3[d.weekday()] + " " + s) if weekday else s


def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mo = (h + l - 7 * m + 114) // 31; da = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(y, mo, da)


def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(wd - d.weekday()) % 7)
    return d + dt.timedelta(days=7 * (n - 1))


# ------------------------------------------------------------------ money
CUR = {  # symbol, prefix?, rate per EUR (approx. 2026), decimals
    "EUR": ("€", True, 1.0, 2), "GBP": ("£", True, 0.86, 2), "USD": ("$", True, 1.12, 2), "CAD": ("C$", True, 1.55, 2),
    "CHF": ("CHF ", True, 0.95, 2), "SEK": (" kr", False, 11.4, 2), "DKK": (" kr", False, 7.46, 2),
    "NOK": (" kr", False, 11.7, 2), "ISK": (" kr", False, 150.0, 0), "PLN": (" zł", False, 4.3, 2),
    "CZK": (" Kč", False, 25.0, 0), "HUF": (" Ft", False, 400.0, 0), "RON": (" lei", False, 5.0, 2)}


def price_end(x, cur, rng):
    """round a raw local price to a retail ending (.99/.49/.95/.79 or whole for 0-decimal currencies)"""
    sym, pre, rate, dec = CUR[cur]
    if dec == 0:
        step = 10 if x > 300 else (5 if x > 50 else 1)
        return float(max(step, int(round(x / step)) * step - (1 if step >= 5 and rng.random() < 0.5 else 0)))
    base = math.floor(x)
    end = rng.choice([0.99, 0.49, 0.95, 0.79, 0.29, 0.89] if cur != "SEK" and cur != "NOK" else [0.90, 0.95, 0.50])
    v = base + end
    if v < 0.5:
        v = 0.49
    return round(v, 2)


def eur_to(x_eur, cur, rng=None, retail=True):
    v = x_eur * CUR[cur][2]
    return price_end(v, cur, rng) if (retail and rng is not None) else round(v, CUR[cur][3])


def money(x, cur):
    sym, pre, rate, dec = CUR[cur]
    s = ("{:,.%df}" % dec).format(x)
    return (sym + s) if pre else (s + sym)


def money_round(x, cur):
    dec = CUR[cur][3]
    return round(x, dec) if dec else float(round(x))


# ------------------------------------------------------------------ units
def oz(g):
    return g / 28.3495


def floz(ml):
    return ml / 29.5735


def us_net(net, unit):
    if unit == "g":
        o = oz(net)
        if o >= 16:
            lb = int(o // 16)
            rest = o - 16 * lb
            return "NET WT %s OZ (%s LB %s OZ) %dg" % (_n1(o), lb, _n1(rest), net) if rest >= 0.05 else "NET WT %s OZ (%d LB) %dg" % (_n1(o), lb, net)
        return "NET WT %s OZ (%dg)" % (_n1(o), net)
    o = floz(net)
    return "%s FL OZ (%s)" % (_n1(o), ("%g L" % (net / 1000)) if net >= 1000 else "%d mL" % net)


def _n1(x):
    s = "%.1f" % x
    return s[:-2] if s.endswith(".0") else s


def eu_net(net, unit):
    if unit == "g":
        return ("%gkg" % (net / 1000)) if net >= 1000 else "%dg" % net
    return ("%gL" % (net / 1000)) if net >= 1000 else ("%dcl" % (net / 10) if net in (250, 330, 500, 750) and False else "%dml" % net)


# ------------------------------------------------------------------ codes
def ean13(rng, prefix):
    body = prefix + "".join(str(rng.randint(0, 9)) for _ in range(12 - len(prefix)))
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(body))
    return body + str((10 - s % 10) % 10)


def upca(rng):
    body = "0" + "".join(str(rng.randint(0, 9)) for _ in range(10))
    s = sum(int(c) * (3 if i % 2 == 0 else 1) for i, c in enumerate(body))
    return body + str((10 - s % 10) % 10)


GS1 = {"UK": "50", "IE": "539", "MT": "535", "DE": "40", "FR": "30", "IT": "80", "ES": "84", "NL": "87", "BE": "54",
       "LU": "54", "PT": "560", "AT": "90", "CH": "76", "DK": "57", "SE": "73", "NO": "70", "FI": "64", "IS": "569",
       "PL": "590", "CZ": "859", "SK": "858", "HU": "599", "SI": "383", "HR": "385", "RO": "594", "BG": "380",
       "GR": "520", "CY": "529", "EE": "474", "LV": "475", "LT": "477"}


def fill_pattern(pat, rng):
    out = []
    for ch in pat:
        if ch == "#":
            out.append(str(rng.randint(0, 9)))
        elif ch == "X":
            out.append(rng.choice("ABDEFGHJLNPQRSTUWXY"))
        else:
            out.append(ch)
    return "".join(out)


LOT_STYLES = ["L YYDDD+A", "L DDMMYY A", "LOT YYMMDD-NN", "L YYYYMMDD A"]


def lot_code(d, style, line, nn):
    """pure function: date + style + line letter + 2-digit run number -> lot string"""
    doy = d.timetuple().tm_yday
    if style == "L YYDDD+A":
        return "L%02d%03d%s" % (d.year % 100, doy, line)
    if style == "L DDMMYY A":
        return "L %s %s" % (d.strftime("%d%m%y"), line)
    if style == "LOT YYMMDD-NN":
        return "LOT %s-%s" % (d.strftime("%y%m%d"), nn)
    return "L%s%s" % (d.strftime("%Y%m%d"), line)


def lot_date(code, style):
    """parse the date encoded in a lot code (QA + ops)"""
    import re
    if style == "L YYDDD+A":
        m = re.match(r"L(\d\d)(\d\d\d)", code)
        y = 2000 + int(m.group(1))
        return dt.date(y, 1, 1) + dt.timedelta(days=int(m.group(2)) - 1)
    if style == "L DDMMYY A":
        m = re.match(r"L (\d\d)(\d\d)(\d\d)", code)
        return dt.date(2000 + int(m.group(3)), int(m.group(2)), int(m.group(1)))
    if style == "LOT YYMMDD-NN":
        m = re.match(r"LOT (\d\d)(\d\d)(\d\d)", code)
        return dt.date(2000 + int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"L(\d{4})(\d\d)(\d\d)", code)
    return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


# ------------------------------------------------------------------ rounding
def r_eu(k, v):
    """EU label rounding (European Commission 2012 guidance on tolerances, used as dataset convention)."""
    if k in ("energy_kj", "energy_kcal"):
        return int(round(v))
    if k == "salt":
        if v >= 1:
            return round(v, 1)
        if v > 0.0125:
            return round(v, 2)
        return 0.0
    if k == "sat":
        if v >= 10:
            return float(round(v))
        if v > 0.1:
            return round(v, 1)
        return 0.0
    if k in ("fat", "carb", "sugar", "protein", "fibre"):
        if v >= 10:
            return float(round(v))
        if v > 0.5:
            return round(v, 1)
        return 0.0
    if k in ("vitd", "vitc", "iron", "calcium", "potassium"):
        return round(v, 1) if v < 10 else float(round(v))
    return round(v, 1)


def g_eu(k, v):
    x = r_eu(k, v)
    if x == 0:
        return {"salt": "<0.01g", "sat": "<0.1g"}.get(k, "<0.5g")
    s = ("%.2f" % x) if (k == "salt" and x < 1) else ("%.1f" % x if x < 10 else "%d" % x)
    return s + "g"


def r_us_cal(c):
    if c < 5:
        return 0
    if c <= 50:
        return int(5 * round(c / 5))
    return int(10 * round(c / 10))


def r_us_fat(v):
    if v < 0.5:
        return 0
    if v < 5:
        return round(v * 2) / 2
    return float(round(v))


def r_us_g(v):
    """carb, fibre, sugars, protein: nearest gram; <0.5 -> 0"""
    return 0 if v < 0.5 else int(round(v))


def r_us_sodium(v):
    if v < 5:
        return 0
    if v <= 140:
        return int(5 * round(v / 5))
    return int(10 * round(v / 10))


def r_us_chol(v):
    return 0 if v < 2 else int(5 * round(v / 5))


def fmt_g(x):
    return ("%g" % x) + "g"


def pct(x):
    return "%d%%" % int(round(x))


def us_temps(s):
    """append Fahrenheit for US text: 'below 25°C' -> 'below 77°F (25°C)'"""
    if not s:
        return s
    def f(m):
        c = float(m.group(1).replace("−", "-"))
        f = c * 9 / 5 + 32
        f = 25 * round(f / 25) if c >= 100 else (5 * round(f / 5) if c >= 50 else round(f))   # ovens: 180°C -> 350°F
        return "%d°F (%s°C)" % (f, m.group(1))
    return re.sub(r"(-?\d+(?:\.\d+)?)\s?°C", f, s)


def the(country):
    return ("the " + country) if country in ("United Kingdom", "United States", "Netherlands", "Czech Republic") else country
