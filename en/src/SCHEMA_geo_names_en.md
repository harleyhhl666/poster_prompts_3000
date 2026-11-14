# Geo + names schema (en/src/lib_geo_en.py, en/src/lib_names_en.py)

## lib_geo_en.py
```python
COUNTRIES = {
  "IE": {"name": "Ireland", "region": "IE", "currency": "EUR", "lang_context": "native",
         "date_style": "eu",           # "eu" = DD/MM/YYYY family, "us" = MM/DD/YYYY family
         "phone_fmt": ["+353 1 5## ####", "01 5## ####"],   # '#' = random digit; fictional-looking ranges
         "postcode_fmt": ["D0# X#X#"],  # letters 'X' random A–Z (engine), '#' digit
         "cities": [ {"city": "Dublin", "area": "County Dublin"}, {"city": "Cork", "area": "County Cork"} ]},   # >= 4 cities
  ...
}
STREETS = { "IE": ["Harbour Road", "Church Lane", ...], ... }   # >= 15 per country, plausible local-language street
         # names (generic types like 'Mill Lane', 'Lindenstraße', 'Rue des Tilleuls'); engine adds a random number
VENUES = { "IE": ["Liffey Quay Community Hall", ...], ... }    # >= 8 per country, FICTIONAL venue names
EN_CONTEXT = { "DE": ["English-language poster at an international supermarket in {city}",
                      "poster for the English-speaking expat community in {city}",
                      "English edition of a store flyer at {city} airport food hall", ...], ... }
         # for every non-Anglophone country: >= 4 realistic reasons the poster/ad is in English; {city} placeholder
```
Required countries (all): UK, IE, MT, US, CA (Anglophone; `lang_context` "native") and DE, FR, NL, BE, LU, ES, PT,
IT, AT, CH, DK, SE, NO, FI, IS, PL, CZ, SK, HU, SI, HR, RO, BG, GR, CY, EE, LV, LT (`lang_context` "international").
UK region "UK", IE region "IE", US region "US", CA region "CA", every other country region "EU".
Currencies: UK GBP, US USD, CA CAD, CH CHF, DK DKK, SE SEK, NO NOK, IS ISK, PL PLN, CZ CZK, HU HUF, RO RON, BG EUR? —
use the currency in force in 2026–27 (BG adopted the euro 1 Jan 2026; HR uses EUR); others EUR.
US/CA cities: give state/province in `area` (e.g. "Columbus, OH"), postcode US "#####", CA "X#X #X#".
UK postcodes like "LS1 4AB" pattern lists; city list must cover England, Scotland, Wales, Northern Ireland.
Phone: US/CA use "(###) 555-01##" (reserved fictional range); UK use "0161 496 0###" / "020 7946 0###" /
"0113 496 0###" (Ofcom drama ranges); others: realistic national format.

## lib_names_en.py
```python
FOOD_BRAND_HEADS = [...]   # >= 120 single words, evocative, multilingual-European flavour ("Hollow Oak", "Fjordlys",
FOOD_BRAND_TAILS = [...]   #  "Valdoro", "Brookmeadow"); TAILS >= 30 ("Farm", "Kitchen", "& Co.", "Dairy", "Bakehouse", "", ...)
HEALTH_BRAND_HEADS = [...] # >= 60 ("Verdalis", "Northwell", "Aurevia"); HEALTH_BRAND_TAILS >= 20 ("Labs", "Health", "Nutrition")
RETAILERS = {"UK": [...], "IE": [...], "US": [...], "CA": [...], "EU": [...]}   # >= 10 each, fictional supermarket /
           # pharmacy / grocery names (e.g. "Greenhill Fresh", "Market & Main", "Northgate Pharmacy")
COMPANY_SUFFIX = {"UK": ["Ltd", "Foods Ltd"], "IE": ["Ltd", "DAC"], "US": ["Inc.", "LLC"], "CA": ["Inc.", "Ltd."],
                  "DE": ["GmbH"], "FR": ["SAS", "SARL"], "IT": ["S.r.l.", "S.p.A."], "ES": ["S.L."], "NL": ["B.V."], ...}  # every country in geo
ORG_PATTERNS = {   # fictional organisers; {city} placeholder
   "city public health department": ["{city} Public Health Partnership", ...],
   "community health partnership": [...], "university health service": [...], "food bank": [...],
   "consumer association": [...], "school": [...], "dietitians' network": [...], "farmers' market association": [...],
   "community centre": [...], "pharmacy": [...], "parish/church": [...], "chamber of commerce": [...],
   "senior citizens' club": [...], "hospital outreach": [...], "food safety council": [...] }   # >= 5 patterns each
FIRST_NAMES = [...]; LAST_NAMES = [...]   # >= 60 each, pan-European + North American mix (speakers)
REAL_BRAND_BLACKLIST = [...]   # >= 250 real food/drink/supplement/retail brands & retailers in Europe/NA (lowercase),
                               # e.g. "tesco", "lidl", "nestle", "nestlé", "kellogg", "heinz", "danone", "centrum" ...
```
Rules: every generated name must avoid real brands (check heads AND tails against the blacklist, including
substrings of length >= 5); avoid real organisations (no "NHS", "FDA", "WHO", "Red Cross" in ORG_PATTERNS).
