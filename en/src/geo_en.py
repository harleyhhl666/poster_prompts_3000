"""Geography / naming helpers on top of lib_geo_en + lib_names_en."""
import re

import common_en as C
import lib_geo_en as G
import lib_names_en as N

ANGLO = {"UK", "IE", "MT", "US", "CA"}
COUNTRY_SHORT = {"US": "USA", "UK": "United Kingdom"}


def country_name(c):
    return G.COUNTRIES[c]["name"]


def city(c, rng):
    return rng.choice(G.COUNTRIES[c]["cities"])


def postcode(c, cty, rng):
    pat = cty.get("postcode") or rng.choice(G.COUNTRIES[c]["postcode_fmt"])
    return C.fill_pattern(pat, rng)


def phone(c, rng, cty=None):
    pat = (cty or {}).get("phone") or rng.choice(G.COUNTRIES[c]["phone_fmt"])
    return C.fill_pattern(pat, rng)


def address(c, rng, cty=None, street=None):
    cty = cty or city(c, rng)
    st = street or rng.choice(G.STREETS[c])
    num = rng.randint(2, 180)
    pc = postcode(c, cty, rng)
    name = COUNTRY_SHORT.get(c, country_name(c))
    if c == "US":
        st_abbr = cty["area"].split(",")[-1].strip()
        city_name = cty["city"].split(",")[0]
        return "%d %s, %s, %s %s, USA" % (num, st, city_name, st_abbr if len(st_abbr) == 2 else cty["area"], pc)
    if c == "CA":
        return "%d %s, %s, %s %s, Canada" % (num, st, cty["city"], cty["area"], pc)
    if c in ("UK", "IE", "MT"):
        return "%d %s, %s %s, %s" % (num, st, cty["city"], pc, name)
    return "%s %d, %s %s, %s" % (st, num, pc, cty["city"], name)


def suffix(c, rng):
    return rng.choice(N.COMPANY_SUFFIX.get(c, ["Ltd"]))


def _clean_name(nm):
    nm = re.sub(r"\b(\w+\.?)( \1)+\b", r"\1", nm)
    words = nm.split()
    out = []
    for w in words:   # drop a repeated generic word anywhere (e.g. 'Kitchen Co. Kitchen plc', 'Fine Foods Foods')
        if w.strip(".").lower() in ("foods", "food", "kitchen", "co", "company", "health", "nutrition") and w.strip(".").lower() in [x.strip(".").lower() for x in out]:
            continue
        out.append(w)
    return " ".join(out).replace("Co. Company", "Co.").replace("Company Co.", "Company")


def company(brand, c, rng, importer=False, health=False):
    cty = city(c, rng)
    if importer:
        base = rng.choice(["%s Trading", "%s Imports", "%s Distribution"] if not health else ["%s Health", "%s Nutrition"]) % brand.split()[0]
    else:
        base = brand if len(brand.split()) > 1 else rng.choice(["%s Foods", "%s Food Company"] if not health else ["%s Laboratories", "%s Nutrition"]) % brand
    suf = [s for s in N.COMPANY_SUFFIX.get(c, ["Ltd"]) if not any(w.strip(".&").lower() in [b.strip(".&").lower() for b in base.split()] for w in s.split() if w.strip(".&"))] or ["Ltd"]
    if "Co." in base or "&" in base:
        suf = [s for s in suf if "&" not in s and "Co" not in s] or ["Ltd"]
    nm = _clean_name("%s %s" % (base, rng.choice(suf)))
    return {"name": nm, "addr": address(c, rng, cty), "country": country_name(c), "cc": c, "city": cty["city"],
            "phone": phone(c, rng, cty)}


def org(kind, c, rng, cty):
    pats = N.ORG_PATTERNS.get(kind) or N.ORG_PATTERNS["community centre"]
    if c in ("US", "CA"):
        pats = [p for p in pats if not re.search(r"Village Hall|Bureau|Parish|Borough|CIC|Trust\b|Council of|Guild", p)] or pats
    return rng.choice(pats).replace("{city}", cty["city"].split(",")[0])


def person(rng):
    return "%s %s" % (rng.choice(N.FIRST_NAMES), rng.choice(N.LAST_NAMES))


def venue(c, rng):
    return rng.choice(G.VENUES[c])


CTX = {"ad": ["English-language edition of the retailer's promotion for international shoppers in {city}",
              "aimed at tourists and international residents shopping in {city}",
              "English version of the store's offer, produced for the many international customers in {city}"],
       "community": ["aimed at the English-speaking international community in {city}",
                     "English-language version for international students and newcomer residents of {city}",
                     "produced in English for expat and international residents of {city}"]}
CTX_KW = {"ad": r"supermarket|shop|store|grocer|airport|station|app|website|online|tourist|market|flyer|deli|food hall|retail",
          "community": r"expat|international|universit|campus|school|communit|student|newcomer|librar|church|club|association|residents"}
CTX_DEFAULT = {"ad": "English edition of the store's promotion for international shoppers in {city}",
               "community": "notice aimed at the English-speaking international community in {city}"}


def en_context(c, rng, cty, kind="ad"):
    """why an English-language poster exists in a non-Anglophone country; filtered to fit the carrier kind"""
    if c in ANGLO:
        return None
    # audience-only wording: place-specific library contexts ('flyer at an international school', 'staff kitchen')
    # contradicted the carrier described in the same prompt
    return rng.choice(CTX[kind]).replace("{city}", cty["city"])


def bump_first_number(s, k):
    m = re.search(r"\d+", s)
    if not m:
        return None, None, None
    n = int(m.group())
    return s[:m.start()] + str(n + k) + s[m.end():], n, n + k


def brand_pool(heads, tails, bl, rng, per_head=1):
    out = []
    pat = re.compile(r"(?<![a-z])(" + "|".join(re.escape(b) for b in bl if len(b) >= 4) + r")(?![a-z])")
    for h in heads:
        for t in tails:
            nm = (h + (" " + t if t else "")).strip()
            low = nm.lower()
            if pat.search(low):
                continue
            out.append(nm)
    rng.shuffle(out)
    seen, res = {}, []
    for nm in out:
        h = nm.split()[0]
        if seen.get(h, 0) >= per_head:
            continue
        seen[h] = seen.get(h, 0) + 1
        res.append(nm)
    return res
