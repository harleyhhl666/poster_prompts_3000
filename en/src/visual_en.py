"""Visual vocab + fixed prompt boilerplate (English)."""

PALETTES = {
    "fresh_blue": "crisp white with sky blue and navy accents", "cream": "warm cream with soft beige and chocolate brown text",
    "meadow_green": "fresh meadow green and white with a touch of lemon yellow", "sunset_orange": "warm orange and coral on off-white",
    "berry": "berry pink and deep plum on white", "cocoa": "rich cocoa brown with gold accents", "festive_red": "festive red, forest green and gold",
    "navy_gold": "deep navy with brushed gold", "lemon": "lemon yellow and charcoal", "mint": "mint green and slate grey",
    "kraft": "natural kraft brown with black type", "black_gold": "matte black with gold foil", "violet_pop": "electric violet and neon lime",
    "sky_gradient": "pale sky-blue to white gradient", "coral": "coral and teal", "forest_copper": "forest green with copper",
    "minimal_grey": "minimal light grey and black", "tomato": "tomato red and cream", "sage": "sage green and oatmeal",
    "nordic": "Nordic white, pale birch wood tones and ink blue", "mediterranean": "Mediterranean terracotta, olive green and white",
    "pastel": "soft pastel peach, lilac and mint"}

STYLES = {
    "label": ["clean supermarket own-label packaging", "premium deli packaging", "minimalist Scandinavian packaging",
              "rustic farmhouse packaging", "modern challenger-brand packaging", "classic heritage packaging"],
    "ad": ["supermarket promotion design", "premium food advertising", "bold discount-store promo", "seasonal retail campaign",
           "clean modern retail design", "playful youth-brand advertising"],
    "supp": ["clinical pharmacy packaging", "premium wellness branding", "natural botanical branding", "sports-nutrition branding",
             "family-friendly vitamin branding"],
    "event": ["community event poster", "modern minimalist event poster", "festive market poster", "campus event poster",
              "retail in-store event poster", "farmers' market chalkboard style"],
    "psa": ["public health campaign poster", "community noticeboard poster", "flat-illustration infographic", "school canteen poster",
            "municipal information poster"]}

REALISM = {"flat": "flat print-ready graphic design, perfectly front-on, even lighting",
           "studio": "photorealistic studio product photograph, soft diffused lighting, sharp focus",
           "scene": "photorealistic in-situ photograph, natural ambient light, sharp focus",
           "phone": "realistic smartphone photo, natural light, sharp focus on the text"}

ARTIFACTS = {
    "soft_shadow": "a soft natural shadow under the main object", "slight_perspective": "a slight camera angle of about 8-10 degrees",
    "plastic_glare": "a gentle glare on the plastic film that does not cover any text", "curved_label": "the label curves naturally around the container",
    "frost": "light frost crystals around the edges, none over the text", "condensation": "a few condensation droplets away from the text",
    "shelf_bg": "a softly blurred supermarket shelf in the background", "clutter_bg": "a kitchen counter with a few out-of-focus items",
    "hand_hold": "the pack is held in one hand, fingers not covering any text", "phone_shot": "slight smartphone vignetting",
    "glass_reflection": "faint reflections on the glass that do not obscure text", "pinned": "pinned to a cork noticeboard with drawing pins",
    "paper_fold": "faint fold lines in the paper"}

QUOTE_RULE = ("Text inside 「」 must appear in the image exactly as written, character for character (do not draw the 「」 brackets "
              "themselves); \u201c|\u201d separates table columns.")
TEXT_RULE = ("All English text, numbers, dates, prices, ingredient lists, nutrition tables, rules and small print must be sharp, complete "
             "and legible. Do not use gibberish, pseudo-letters, lorem ipsum, random symbols or blurred placeholder text; do not omit, "
             "abbreviate, reword, add to or 'correct' any given number, date, code or field; do not add any other readable text "
             "(decorative textures excepted).")
TABLE_RULE = ("Draw the nutrition/facts table as a complete ruled table with aligned rows and columns, every value with its unit; print "
              "the ingredient list in full in exactly the given order.")
CAPS_RULE = "Words written in CAPITALS inside the ingredient list are allergen emphasis and must be printed in bold capitals."
FONT_RULE = "Headlines in a bold sans-serif; body text and tables in a clean, highly legible sans-serif; the smallest text at least 1.2% of the image height."

TAMPER_NOTE = ("This is a research sample: some of the given text ({fields}) deliberately contains information that is false, exaggerated, "
               "missing or inconsistent with other parts of the image. Reproduce every given text exactly; do not correct, complete or "
               "harmonise anything, and do not highlight these parts with colour, circles, arrows, enlargement, strike-through or any "
               "warning mark. They must use the same font, size and style as the surrounding text, so the whole image looks like a "
               "completely normal {kind}.")
CLEAN_NOTE = "This is the normal reference version: render every field exactly as given."
FIELD_NAMES = {"efficacy_exaggeration": "health claims", "allergen_deletion": "allergen information", "production_date_tamper": "dates and lot code",
               "shelf_life_tamper": "shelf life and dates", "ingredient_order_tamper": "ingredient list", "nutrition_value_tamper": "nutrition table",
               "claim_nutrition_conflict": "nutrition claims", "quantity_tamper": "net quantity", "batch_number_tamper": "lot code",
               "manufacturer_info_tamper": "producer details", "storage_condition_tamper": "storage instructions",
               "product_attribute_tamper": "product badges", "target_population_tamper": "suitability statement",
               "warning_deletion": "warnings", "price_tamper": "prices", "promotion_date_tamper": "offer dates",
               "promotion_rule_tamper": "offer rules", "hidden_fee_condition": "offer conditions", "quota_contradiction": "quantities/places",
               "regulatory_status_tamper": "regulatory status", "function_upgrade": "claims", "unsubstantiated_claim": "claims",
               "health_fact_tamper": "health facts", "misinformation_insertion": "advice sections", "event_date_tamper": "dates",
               "venue_tamper": "addresses", "agenda_time_conflict": "programme times", "contact_info_tamper": "phone numbers",
               "source_attribution_tamper": "source line"}
