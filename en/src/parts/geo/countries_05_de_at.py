# Germany and Austria.
COUNTRIES = {
    "DE": {"name": "Germany", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+49 30 ### ####", "030 ### ####", "089 ### ####", "+49 40 ### ####", "0221 ### ####"],
           "postcode_fmt": ["#####"],
           "cities": [
               {"city": "Berlin", "area": "Berlin", "postcode": "104##", "phone": "030 ### ####"},
               {"city": "Hamburg", "area": "Hamburg", "postcode": "220##", "phone": "040 ### ####"},
               {"city": "Munich", "area": "Bavaria", "postcode": "803##", "phone": "089 ### ####"},
               {"city": "Nuremberg", "area": "Bavaria", "postcode": "904##", "phone": "0911 ### ####"},
               {"city": "Cologne", "area": "North Rhine-Westphalia", "postcode": "506##", "phone": "0221 ### ####"},
               {"city": "Münster", "area": "North Rhine-Westphalia", "postcode": "481##", "phone": "0251 ### ####"},
               {"city": "Frankfurt am Main", "area": "Hesse", "postcode": "603##", "phone": "069 ### ####"},
               {"city": "Stuttgart", "area": "Baden-Württemberg", "postcode": "701##", "phone": "0711 ### ####"},
               {"city": "Freiburg im Breisgau", "area": "Baden-Württemberg", "postcode": "791##", "phone": "0761 ### ####"},
               {"city": "Heidelberg", "area": "Baden-Württemberg", "postcode": "691##", "phone": "06221 ### ###"},
               {"city": "Leipzig", "area": "Saxony", "postcode": "041##", "phone": "0341 ### ####"},
               {"city": "Dresden", "area": "Saxony", "postcode": "011##", "phone": "0351 ### ####"},
               {"city": "Hanover", "area": "Lower Saxony", "postcode": "301##", "phone": "0511 ### ####"},
               {"city": "Bremen", "area": "Bremen", "postcode": "282##", "phone": "0421 ### ####"},
               {"city": "Mainz", "area": "Rhineland-Palatinate", "postcode": "551##", "phone": "06131 ### ###"},
               {"city": "Kiel", "area": "Schleswig-Holstein", "postcode": "241##", "phone": "0431 ### ####"},
               {"city": "Erfurt", "area": "Thuringia", "postcode": "990##", "phone": "0361 ### ####"},
               {"city": "Rostock", "area": "Mecklenburg-Western Pomerania", "postcode": "180##", "phone": "0381 ### ####"}]},
    "AT": {"name": "Austria", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["01 ### ####", "+43 1 ### ####", "0316 ### ###", "0662 ### ###", "+43 664 ### ####"],
           "postcode_fmt": ["####"],
           "cities": [
               {"city": "Vienna", "area": "Vienna", "postcode": "11#0", "phone": "01 ### ####"},
               {"city": "Graz", "area": "Styria", "postcode": "8010", "phone": "0316 ### ###"},
               {"city": "Linz", "area": "Upper Austria", "postcode": "4020", "phone": "0732 ### ###"},
               {"city": "Salzburg", "area": "Salzburg", "postcode": "5020", "phone": "0662 ### ###"},
               {"city": "Innsbruck", "area": "Tyrol", "postcode": "6020", "phone": "0512 ### ###"},
               {"city": "Klagenfurt", "area": "Carinthia", "postcode": "9020", "phone": "0463 ### ###"},
               {"city": "Villach", "area": "Carinthia", "postcode": "9500", "phone": "04242 ## ###"},
               {"city": "St. Pölten", "area": "Lower Austria", "postcode": "3100", "phone": "02742 ## ###"},
               {"city": "Bregenz", "area": "Vorarlberg", "postcode": "6900", "phone": "05574 ## ###"},
               {"city": "Wels", "area": "Upper Austria", "postcode": "4600", "phone": "07242 ## ###"}]},
}

STREETS = {
    "DE": ["Lindenstraße", "Schulstraße", "Gartenweg", "Kirchgasse", "Mühlenweg", "Birkenallee", "Am Marktplatz",
           "Rosenstraße", "Ahornweg", "Feldstraße", "Bergstraße", "Wiesenweg", "Goethestraße", "Am Mühlbach",
           "Talstraße", "Brunnenstraße", "Uferweg", "Eichendorffstraße"],
    "AT": ["Hauptstraße", "Lindengasse", "Kirchengasse", "Mühlweg", "Schulgasse", "Gartengasse", "Am Anger",
           "Rosengasse", "Feldgasse", "Bergweg", "Wiesengasse", "Brunnengasse", "Waldweg", "Dorfplatz", "Erlenweg",
           "Sonnenweg"]}

VENUES = {
    "DE": ["Bürgerhaus Lindenhain", "Stadtteilzentrum Am Mühlbach", "Markthalle Nordviertel",
           "Hörsaalgebäude West, Campus Talaue", "Gemeindesaal St. Ansgar", "Stadtteilbibliothek Kastanienhof",
           "Einkaufszentrum Weidenpark", "Familienzentrum Sonnenhof", "Begegnungsstätte Birkenhain"],
    "AT": ["Volkshaus Lindenau", "Pfarrsaal St. Florian Süd", "Bauernmarkt am Anger", "Hörsaalzentrum Campus Nord",
           "Stadtteilbibliothek Erlenhof", "Einkaufszentrum Talblick", "Seniorentreff Sonnenhof",
           "Kulturhaus am Mühlbach", "Gemeindezentrum Rosengasse"]}

EN_CONTEXT = {
    "DE": ["English-language poster at an international supermarket in {city}",
           "notice for the English-speaking expat community in {city}",
           "flyer on the noticeboard of an international school in {city}",
           "poster on the {city} university campus aimed at international students",
           "English edition of a grocery delivery app banner shown in {city}",
           "food-hall advert at {city} airport"],
    "AT": ["poster for the English-speaking expat association in {city}",
           "flyer at an international school in {city}",
           "English-language notice at a university campus in {city} for exchange students",
           "advert in the tourist old town of {city} aimed at international visitors",
           "English edition of a supermarket loyalty app used in {city}"]}
