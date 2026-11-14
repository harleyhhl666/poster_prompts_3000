# Event + public-service poster schemas (en/src/lib_event_en.py, en/src/lib_psa_en.py)

All text English. Settings span Europe (EU/EEA, UK, Switzerland) and North America (US, Canada).
English must be natural for the setting: Anglophone countries, or international/expat/university/tourist
contexts in continental Europe (the engine adds that context sentence). ALL organisers, brands, venues fictional.
Real public bodies may only appear as a *source line* for a verified fact (e.g. "Source: WHO, Healthy diet fact sheet").

Region groups: "US", "CA", "UK", "IE", "EU" (EU = continental Europe incl. Malta, Switzerland, Norway, Iceland).
Season keys: any, autumn, winter, spring, halloween, ca_thanksgiving, us_thanksgiving, black_friday, st_martin,
sinterklaas, christmas_market, christmas, new_year, veganuary, burns_night, valentines, carnival, pancake_day,
mothers_day_uk, st_patricks, easter.  (engine owns the actual date windows, Oct 2026 – Apr 2027)

## lib_event_en.py -> `EVENTS = [ {...} ]` (target >= 30, varied sub_category)
```python
{
 "id": "e_yogurt_tasting",
 "sub_category": "In-store tasting",  # In-store tasting | Product launch | Health talk | Nutrition workshop |
   # Cooking class | Kids' cooking club | Farmers' market | Christmas market | Food festival | Charity bake sale |
   # Food bank drive | Free health check | Supplement info session | Store opening | Member day | Store anniversary |
   # Coffee cupping | Cheese & bread tasting | Chocolate workshop | Campus health week | Workplace wellness day |
   # Food safety week | Community supper | Seasonal pop-up | Trade fair | Baking class   (extend if needed)
 "commercial": True,
 "regions": ["UK", "IE", "US", "CA", "EU"],
 "season": "any",
 "title_patterns": ["{brand} Greek Yogurt Tasting Week", "Taste the New {brand} Skyr Range"],  # {brand} or {city} only
 "subtitle": "Try three new flavours — free samples while stocks last",
 "product_hint": "flavoured yogurt",   # or None
 "agenda": [["10:00", "10:30", "Meet the makers"], ["10:30", "12:30", "Free tasting at the dairy aisle"]],  # 3–6 slots, 24h
 "perks": ["Free sample cup for every visitor", "Scan to join and get 10% off your next shop"],   # 2–4
 "rules": ["One sample per person", "Samples while stocks last", "Under-16s must be accompanied by an adult"],  # 2–4
 "hidden_condition": "Samples are only available with a minimum spend of {money:15}",  # hidden paid condition
 "quota": 200,                  # participants / gifts (int)
 "fee_eur": 0,                  # 0 = free; else price in EUR (engine converts to local currency)
 "venue_types": ["supermarket dairy aisle", "shopping centre atrium"],
 "duration_days": [2, 5],
 "daily_hours": ["10:00–18:00", "11:00–19:00"],
 "speaker_roles": None,         # e.g. ["registered dietitian", "GP", "pharmacist"] for talks
 "health_related": False,
 "disclaimer": None,            # compliant line for health events, e.g. "This talk is educational and does not replace medical advice."
 "exag_line": None,             # strong illegal promise for health/supplement events, e.g. "Buy today and stop taking your blood-pressure pills"
 "registration": "Book online or at the customer service desk",
 "visual_styles": ["supermarket promo", "fresh minimalist"],
 "visual_motif": "white yogurt pots, blueberries, marble counter",
}
```
`{money:15}` = an amount in EUR the engine converts; usable in hidden_condition / perks / rules.

## lib_psa_en.py -> `PSA = [ {...} ]` (target >= 30 themes)
```python
{
 "id": "p_salt_reduction",
 "sub_category": "Salt reduction",  # Food safety at home | Salt reduction | Sugar reduction | Allergen awareness |
   # Food waste | Date labels | Supplement scams (older adults) | Reading nutrition labels | Hand hygiene |
   # Holiday food safety | Wild mushroom poisoning | Fridge & leftovers | School food | Healthy drinks |
   # Online food shopping | Food fraud | Barbecue/grill safety | Raw milk & cheese risks | Pregnancy food safety |
   # Healthy ageing nutrition | Infant feeding safety | Food bank & food poverty | Water & hydration  (extend)
 "regions": ["UK", "IE", "EU"],
 "season": "any",
 "titles": ["Shake the Salt Habit", "Less Salt, More Life"],
 "subtitles": ["Adults should eat no more than 6g of salt a day"],
 "organizer_types": ["city public health department", "community health partnership", "university health service"],
 "sections": [ {"heading": "Why cut down?", "items": ["...", "..."]},   # 3–5 sections x 3–6 items, <= 90 chars each
               {"heading": "Easy swaps", "items": ["..."]} ],
 "numbers": [ {"text": "Adults should eat no more than 6g of salt a day",
               "tampered": "Adults should eat no more than 16g of salt a day",
               "fact_id": "nhs_salt_6g"} ],      # text must appear verbatim in a section item or subtitle
 "key_warning": "If you have high blood pressure, follow your doctor's advice on salt.",
 "misinfo_subtle": "Sea salt contains less sodium than table salt, so you can use more",
 "misinfo_strong": "Drinking lemon water every morning flushes excess salt out of your body",
 "cta": "Scan the QR code to take the 4-week salt swap challenge",
 "has_event": True, "event_kinds": ["free blood pressure check", "healthy cooking demo"],
 "visual_styles": ["public health campaign", "community noticeboard"],
 "visual_motif": "salt shaker, fresh herbs, heart icon",
}
```
Quantitative facts allowed ONLY from refs/facts_whitelist.md (use the exact `fact_id`); every number in `sections`,
`subtitles` must come from that list or be non-numeric advice. Facts are region-specific (°F + FDA/USDA for US,
°C + NHS/FSA for UK, WHO for anywhere) — set `regions` accordingly. Misinformation is realistic rumour style,
never absurd; it must be clearly false to an expert.
