# Poland and Czechia.
COUNTRIES = {
    "PL": {"name": "Poland", "region": "EU", "currency": "PLN", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["22 ### ## ##", "+48 22 ### ## ##", "12 ### ## ##", "+48 5## ### ###", "+48 6## ### ###"],
           "postcode_fmt": ["##-###"],
           "cities": [{"city": "Warsaw", "area": "Masovian Voivodeship", "postcode": "02-###", "phone": "22 ### ## ##"},
                      {"city": "Kraków", "area": "Lesser Poland Voivodeship", "postcode": "31-###", "phone": "12 ### ## ##"},
                      {"city": "Wrocław", "area": "Lower Silesian Voivodeship", "postcode": "50-###", "phone": "71 ### ## ##"},
                      {"city": "Gdańsk", "area": "Pomeranian Voivodeship", "postcode": "80-###", "phone": "58 ### ## ##"},
                      {"city": "Poznań", "area": "Greater Poland Voivodeship", "postcode": "60-###", "phone": "61 ### ## ##"},
                      {"city": "Łódź", "area": "Łódź Voivodeship", "postcode": "90-###", "phone": "42 ### ## ##"},
                      {"city": "Lublin", "area": "Lublin Voivodeship", "postcode": "20-###", "phone": "81 ### ## ##"},
                      {"city": "Katowice", "area": "Silesian Voivodeship", "postcode": "40-###", "phone": "32 ### ## ##"},
                      {"city": "Szczecin", "area": "West Pomeranian Voivodeship", "postcode": "70-###", "phone": "91 ### ## ##"},
                      {"city": "Toruń", "area": "Kuyavian-Pomeranian Voivodeship", "postcode": "87-1##", "phone": "56 ### ## ##"},
                      {"city": "Rzeszów", "area": "Subcarpathian Voivodeship", "postcode": "35-0##", "phone": "17 ### ## ##"},
                      {"city": "Białystok", "area": "Podlaskie Voivodeship", "postcode": "15-###", "phone": "85 ### ## ##"}]},
    "CZ": {"name": "Czechia", "region": "EU", "currency": "CZK", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+420 2## ### ###", "2## ### ###", "+420 5## ### ###", "+420 6## ### ###", "7## ### ###"],
           "postcode_fmt": ["### ##"],
           "cities": [{"city": "Prague", "area": "Prague", "postcode": "1#0 00", "phone": "2## ### ###"},
                      {"city": "Brno", "area": "South Moravian Region", "postcode": "602 00", "phone": "54# ### ###"},
                      {"city": "Ostrava", "area": "Moravian-Silesian Region", "postcode": "702 00", "phone": "59# ### ###"},
                      {"city": "Plzeň", "area": "Plzeň Region", "postcode": "301 00", "phone": "37# ### ###"},
                      {"city": "Olomouc", "area": "Olomouc Region", "postcode": "779 00", "phone": "58# ### ###"},
                      {"city": "Liberec", "area": "Liberec Region", "postcode": "460 01", "phone": "48# ### ###"},
                      {"city": "České Budějovice", "area": "South Bohemian Region", "postcode": "370 01", "phone": "38# ### ###"},
                      {"city": "Hradec Králové", "area": "Hradec Králové Region", "postcode": "500 02", "phone": "49# ### ###"},
                      {"city": "Pardubice", "area": "Pardubice Region", "postcode": "530 02", "phone": "46# ### ###"},
                      {"city": "Zlín", "area": "Zlín Region", "postcode": "760 01", "phone": "57# ### ###"}]},
}

STREETS = {
    "PL": ["ul. Lipowa", "ul. Szkolna", "ul. Kościelna", "ul. Ogrodowa", "ul. Polna", "ul. Leśna", "ul. Słoneczna",
           "ul. Kwiatowa", "ul. Brzozowa", "ul. Klonowa", "ul. Krótka", "ul. Młyńska", "ul. Spacerowa",
           "ul. Akacjowa", "ul. Parkowa", "ul. Dworcowa", "ul. Zielona"],
    "CZ": ["Školní", "Nádražní", "Lipová", "Zahradní", "Krátká", "Polní", "Kostelní", "Luční", "Mlýnská", "Husova",
           "Komenského", "Na Výsluní", "Lesní", "Sadová", "Palackého", "Bezručova", "Jabloňová"]}

VENUES = {
    "PL": ["Dom Kultury Lipowy Gaj", "Klub Seniora Pod Klonem", "Hala Targowa Przy Młynie",
           "Biblioteka Osiedlowa Brzozowa", "Aula Główna, Kampus Zielony", "Centrum Handlowe Słoneczne Wzgórze",
           "Sala Parafialna św. Wojciecha", "Centrum Sąsiedzkie Akacjowa", "Hala Sportowa Parkowa"],
    "CZ": ["Komunitní centrum Lipka", "Kulturní dům Na Výsluní", "Tržnice U Mlýna", "Knihovna Sadová",
           "Aula kampusu Luční", "Obchodní centrum Zahrada", "Farní sál sv. Václava", "Klub seniorů Polní",
           "Sokolovna Jabloňová"]}

EN_CONTEXT = {
    "PL": ["poster on the {city} university campus for Erasmus and English-taught programme students",
           "flyer at an international school in {city}",
           "staff-kitchen poster at an international business-services office in {city}",
           "advert in the tourist old town of {city}",
           "English edition of a grocery delivery app banner shown in {city}"],
    "CZ": ["advert in the tourist old town of {city}",
           "poster on the {city} university campus for international students",
           "flyer at an international school in {city}",
           "notice for the English-speaking expat community in {city}",
           "food-court advert at {city} airport or main railway station"]}
