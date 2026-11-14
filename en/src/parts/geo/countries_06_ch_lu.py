# Switzerland and Luxembourg.
COUNTRIES = {
    "CH": {"name": "Switzerland", "region": "EU", "currency": "CHF", "lang_context": "international",
           "date_style": "eu",
           "phone_fmt": ["044 ### ## ##", "+41 44 ### ## ##", "+41 22 ### ## ##", "061 ### ## ##", "031 ### ## ##",
                         "+41 79 ### ## ##"],
           "postcode_fmt": ["####"],
           "cities": [
               {"city": "Zurich", "area": "Canton of Zurich", "postcode": "80##", "phone": "044 ### ## ##"},
               {"city": "Winterthur", "area": "Canton of Zurich", "postcode": "840#", "phone": "052 ### ## ##"},
               {"city": "Geneva", "area": "Canton of Geneva", "postcode": "120#", "phone": "022 ### ## ##"},
               {"city": "Basel", "area": "Basel-Stadt", "postcode": "405#", "phone": "061 ### ## ##"},
               {"city": "Bern", "area": "Canton of Bern", "postcode": "300#", "phone": "031 ### ## ##"},
               {"city": "Lausanne", "area": "Vaud", "postcode": "100#", "phone": "021 ### ## ##"},
               {"city": "Lucerne", "area": "Canton of Lucerne", "postcode": "600#", "phone": "041 ### ## ##"},
               {"city": "St. Gallen", "area": "Canton of St. Gallen", "postcode": "900#", "phone": "071 ### ## ##"},
               {"city": "Lugano", "area": "Ticino", "postcode": "690#", "phone": "091 ### ## ##"},
               {"city": "Zug", "area": "Canton of Zug", "postcode": "6300", "phone": "041 ### ## ##"}]},
    "LU": {"name": "Luxembourg", "region": "EU", "currency": "EUR", "lang_context": "international",
           "date_style": "eu",
           "phone_fmt": ["+352 26 ## ## ##", "+352 ## ## ##", "+352 621 ### ###", "26 ## ## ##"],
           "postcode_fmt": ["L-####"],
           "cities": [
               {"city": "Luxembourg City", "area": "Canton of Luxembourg", "postcode": "L-1###", "phone": "+352 22 ## ##"},
               {"city": "Esch-sur-Alzette", "area": "Canton of Esch-sur-Alzette", "postcode": "L-41##", "phone": "+352 54 ## ##"},
               {"city": "Dudelange", "area": "Canton of Esch-sur-Alzette", "postcode": "L-34##", "phone": "+352 51 ## ##"},
               {"city": "Ettelbruck", "area": "Canton of Diekirch", "postcode": "L-90##", "phone": "+352 81 ## ##"},
               {"city": "Diekirch", "area": "Canton of Diekirch", "postcode": "L-92##", "phone": "+352 80 ## ##"},
               {"city": "Echternach", "area": "Canton of Echternach", "postcode": "L-64##", "phone": "+352 72 ## ##"},
               {"city": "Mersch", "area": "Canton of Mersch", "postcode": "L-75##", "phone": "+352 32 ## ##"},
               {"city": "Remich", "area": "Canton of Remich", "postcode": "L-55##", "phone": "+352 23 ## ##"}]},
}

STREETS = {
    "CH": ["Kirchgasse", "Dorfstrasse", "Lindenweg", "Gartenstrasse", "Seestrasse", "Rosenweg", "Mühleweg",
           "Schulhausstrasse", "Bergstrasse", "Rue des Tilleuls", "Chemin des Vignes", "Avenue de la Gare",
           "Rue du Marché", "Chemin du Moulin", "Via dei Castagni", "Via alla Chiesa", "Bachweg"],
    "LU": ["Rue de l'Église", "Rue des Prés", "Rue du Moulin", "Rue de la Gare", "Rue des Jardins", "Rue du Marché",
           "Rue des Champs", "Rue des Vignes", "Rue Principale", "Rue de la Montagne", "Rue des Romains",
           "Rue des Hêtres", "Rue Belle-Vue", "Am Bongert", "Kiirchestrooss", "Rue du Château"]}

VENUES = {
    "CH": ["Quartiertreff Birkenrain", "Salle communale des Tilleuls", "Markthalle am Seeufer",
           "Hörsaalgebäude Campus Rosental", "Bibliothèque de quartier des Vignes", "Centro civico Castagneto",
           "Einkaufszentrum Talacker", "Kirchgemeindehaus Seerose", "Gemeinschaftszentrum Bachmatt"],
    "LU": ["Centre culturel Am Bongert", "Salle des fêtes des Prés", "Marché couvert Belle-Vue",
           "Bibliothèque communale des Hêtres", "Centre commercial Les Romains", "Hall sportif du Moulin",
           "Maison de quartier Sainte-Barbe", "Foyer seniors Rue des Prés", "Auditoire 2, Campus des Jardins"]}

EN_CONTEXT = {
    "CH": ["poster for the English-speaking community of international-organisation staff in {city}",
           "flyer at an international school in {city}",
           "staff-canteen notice on a multinational company campus in {city}",
           "English edition of a supermarket app promotion shown in {city}",
           "advert in the departures food court at {city} airport or main railway station",
           "poster in the tourist old town of {city}"],
    "LU": ["notice for EU-institution staff and families in {city}",
           "flyer at a European School campus in {city}",
           "poster for the English-speaking expat association in {city}",
           "English-language advert at an international supermarket in {city}",
           "noticeboard poster at the university campus near {city} for international students"]}
