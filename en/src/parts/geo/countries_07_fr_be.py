# France and Belgium.
COUNTRIES = {
    "FR": {"name": "France", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["01 99 00 ## ##", "+33 1 99 00 ## ##", "02 61 91 ## ##", "03 53 01 ## ##", "04 65 71 ## ##",
                         "05 36 49 ## ##", "06 39 98 ## ##"],
           "postcode_fmt": ["#####"],
           "cities": [
               {"city": "Paris", "area": "Île-de-France", "postcode": "7501#", "phone": "01 99 00 ## ##"},
               {"city": "Lyon", "area": "Auvergne-Rhône-Alpes", "postcode": "6900#", "phone": "04 65 71 ## ##"},
               {"city": "Grenoble", "area": "Auvergne-Rhône-Alpes", "postcode": "38000", "phone": "04 65 71 ## ##"},
               {"city": "Marseille", "area": "Provence-Alpes-Côte d'Azur", "postcode": "1300#", "phone": "04 65 71 ## ##"},
               {"city": "Nice", "area": "Provence-Alpes-Côte d'Azur", "postcode": "06000", "phone": "04 65 71 ## ##"},
               {"city": "Toulouse", "area": "Occitanie", "postcode": "31000", "phone": "05 36 49 ## ##"},
               {"city": "Montpellier", "area": "Occitanie", "postcode": "34000", "phone": "04 65 71 ## ##"},
               {"city": "Bordeaux", "area": "Nouvelle-Aquitaine", "postcode": "33000", "phone": "05 36 49 ## ##"},
               {"city": "Lille", "area": "Hauts-de-France", "postcode": "59000", "phone": "03 53 01 ## ##"},
               {"city": "Nantes", "area": "Pays de la Loire", "postcode": "44000", "phone": "02 61 91 ## ##"},
               {"city": "Strasbourg", "area": "Grand Est", "postcode": "67000", "phone": "03 53 01 ## ##"},
               {"city": "Rennes", "area": "Brittany", "postcode": "35000", "phone": "02 61 91 ## ##"},
               {"city": "Dijon", "area": "Bourgogne-Franche-Comté", "postcode": "21000", "phone": "03 53 01 ## ##"},
               {"city": "Rouen", "area": "Normandy", "postcode": "76000", "phone": "02 61 91 ## ##"},
               {"city": "Tours", "area": "Centre-Val de Loire", "postcode": "37000", "phone": "02 61 91 ## ##"}]},
    "BE": {"name": "Belgium", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["02 ### ## ##", "+32 2 ### ## ##", "03 ### ## ##", "09 ### ## ##", "+32 47# ## ## ##"],
           "postcode_fmt": ["####"],
           "cities": [
               {"city": "Brussels", "area": "Brussels-Capital Region", "postcode": "1000", "phone": "02 ### ## ##"},
               {"city": "Antwerp", "area": "Antwerp", "postcode": "2000", "phone": "03 ### ## ##"},
               {"city": "Mechelen", "area": "Antwerp", "postcode": "2800", "phone": "015 ## ## ##"},
               {"city": "Ghent", "area": "East Flanders", "postcode": "9000", "phone": "09 ### ## ##"},
               {"city": "Bruges", "area": "West Flanders", "postcode": "8000", "phone": "050 ## ## ##"},
               {"city": "Leuven", "area": "Flemish Brabant", "postcode": "3000", "phone": "016 ## ## ##"},
               {"city": "Liège", "area": "Liège", "postcode": "4000", "phone": "04 ### ## ##"},
               {"city": "Namur", "area": "Namur", "postcode": "5000", "phone": "081 ## ## ##"},
               {"city": "Charleroi", "area": "Hainaut", "postcode": "6000", "phone": "071 ## ## ##"},
               {"city": "Mons", "area": "Hainaut", "postcode": "7000", "phone": "065 ## ## ##"},
               {"city": "Hasselt", "area": "Limburg", "postcode": "3500", "phone": "011 ## ## ##"}]},
}

STREETS = {
    "FR": ["Rue des Tilleuls", "Rue de la Mairie", "Rue du Moulin", "Rue des Écoles", "Avenue de la Gare",
           "Rue Victor Hugo", "Rue Pasteur", "Place du Marché", "Rue des Lilas", "Chemin des Vignes", "Rue du Lavoir",
           "Allée des Peupliers", "Rue Jean Jaurès", "Rue de la Fontaine", "Impasse des Roses", "Rue des Acacias",
           "Boulevard de la Liberté"],
    "BE": ["Kerkstraat", "Stationsstraat", "Molenstraat", "Schoolstraat", "Lindenlaan", "Dorpsstraat", "Kapelstraat",
           "Beukenlaan", "Bosstraat", "Nieuwstraat", "Rue de l'Église", "Rue de la Station", "Rue du Moulin",
           "Avenue des Tilleuls", "Rue des Écoles", "Rue des Champs"]}

VENUES = {
    "FR": ["Salle des fêtes des Tilleuls", "Maison de quartier Les Peupliers", "Marché couvert du Lavoir",
           "Médiathèque des Acacias", "Centre commercial Les Arcades Fleuries", "Amphithéâtre B, Campus des Lilas",
           "Espace associatif La Fontaine", "Halle aux producteurs de la Mairie", "Foyer des Anciens Jean Jaurès"],
    "BE": ["Gemeenschapscentrum De Linde", "Ontmoetingscentrum Molenhof", "Overdekte Markt Kapelhof",
           "Bibliotheek Beukenhof", "Maison de quartier Les Tilleuls", "Salle polyvalente du Moulin",
           "Aula Campus Zuid", "Winkelcentrum De Vlasbloem", "Parochiezaal Sint-Jozef"]}

EN_CONTEXT = {
    "FR": ["English-language poster for the Anglophone expat association in {city}",
           "flyer at an international school (bilingual section) in {city}",
           "poster on the {city} university campus for Erasmus and exchange students",
           "advert in the tourist old town of {city} aimed at English-speaking visitors",
           "English edition of a grocery delivery app banner shown in {city}",
           "airport food-court poster at {city} airport"],
    "BE": ["notice for EU-institution and international-organisation staff in {city}",
           "flyer at a European School or international school in {city}",
           "poster on the {city} university campus for international students",
           "English-language advert at an international supermarket in {city}",
           "poster in the historic centre of {city} for English-speaking tourists"]}
