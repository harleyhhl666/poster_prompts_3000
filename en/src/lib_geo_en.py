"""Geography library for the English (Europe + North America) poster-prompt engine.

Schema: en/src/SCHEMA_geo_names_en.md.  Data lives in en/src/parts/geo/countries_*.py; each part file defines
COUNTRIES, STREETS, VENUES, EN_CONTEXT for a few countries.  This module merges them (lists deduplicated).

Optional extra keys per city (engine may ignore): "postcode" (pattern matching the city, '#'=digit, 'X'=letter)
and "phone" (pattern using a fictional / drama range local to that city).
"""
import glob
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_PART_GLOB = os.path.join(_HERE, "parts", "geo", "countries_*.py")

COUNTRIES = {}
STREETS = {}
VENUES = {}
EN_CONTEXT = {}


def _load(path):
    name = "_lib_geo_en_part_" + os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dedupe(seq):
    seen, out = set(), []
    for x in seq:
        k = repr(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def _merge():
    for path in sorted(glob.glob(_PART_GLOB)):
        mod = _load(path)
        for target, attr in ((COUNTRIES, "COUNTRIES"), (STREETS, "STREETS"), (VENUES, "VENUES"),
                             (EN_CONTEXT, "EN_CONTEXT")):
            for code, val in getattr(mod, attr, {}).items():
                if isinstance(val, list):
                    target[code] = _dedupe(target.get(code, []) + list(val))
                elif isinstance(val, dict) and isinstance(target.get(code), dict):
                    target[code].update(val)
                else:
                    target[code] = val
    for d in COUNTRIES.values():
        d["cities"] = _dedupe(d.get("cities", []))


_merge()

ANGLOPHONE = sorted(c for c, d in COUNTRIES.items() if d.get("lang_context") == "native")
INTERNATIONAL = sorted(c for c, d in COUNTRIES.items() if d.get("lang_context") == "international")


def countries_in_region(region):
    """Country codes whose `region` equals region ("UK", "IE", "US", "CA", "EU"); MT is region "EU"."""
    return sorted(c for c, d in COUNTRIES.items() if d.get("region") == region)
