"""Fictional-name pools for the English (Europe + North America) poster-prompt engine.

Schema: en/src/SCHEMA_geo_names_en.md.  Data lives in en/src/parts/names/*.py; each part file defines any subset
of the exported names below.  Lists are concatenated and deduplicated (REAL_BRAND_BLACKLIST is lower-cased);
dicts are merged key by key, with list values concatenated and deduplicated.
"""
import glob
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_PART_GLOB = os.path.join(_HERE, "parts", "names", "*.py")

_LISTS = ["FOOD_BRAND_HEADS", "FOOD_BRAND_TAILS", "HEALTH_BRAND_HEADS", "HEALTH_BRAND_TAILS",
          "FIRST_NAMES", "LAST_NAMES", "REAL_BRAND_BLACKLIST"]
_DICTS = ["RETAILERS", "COMPANY_SUFFIX", "ORG_PATTERNS"]

FOOD_BRAND_HEADS = []
FOOD_BRAND_TAILS = []
HEALTH_BRAND_HEADS = []
HEALTH_BRAND_TAILS = []
RETAILERS = {}
COMPANY_SUFFIX = {}
ORG_PATTERNS = {}
FIRST_NAMES = []
LAST_NAMES = []
REAL_BRAND_BLACKLIST = []


def _load(path):
    name = "_lib_names_en_part_" + os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _merge():
    g = globals()
    for path in sorted(glob.glob(_PART_GLOB)):
        if os.path.basename(path).startswith("_"):
            continue
        mod = _load(path)
        for k in _LISTS:
            g[k].extend(getattr(mod, k, []))
        for k in _DICTS:
            for key, val in getattr(mod, k, {}).items():
                g[k][key] = _dedupe(g[k].get(key, []) + list(val))
    for k in _LISTS:
        vals = [v.strip() for v in g[k]]
        if k == "REAL_BRAND_BLACKLIST":
            vals = [v.lower() for v in vals]
        g[k][:] = _dedupe(vals)


_merge()
