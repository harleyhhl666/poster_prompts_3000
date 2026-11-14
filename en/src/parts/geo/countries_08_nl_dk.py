# Netherlands and Denmark.
COUNTRIES = {
    "NL": {"name": "Netherlands", "region": "EU", "currency": "EUR", "lang_context": "international",
           "date_style": "eu",
           "phone_fmt": ["020 ### ####", "+31 20 ### ####", "010 ### ####", "030 ### ####", "06 ## ## ## ##"],
           "postcode_fmt": ["#### XX"],
           "cities": [
               {"city": "Amsterdam", "area": "North Holland", "postcode": "101# XX", "phone": "020 ### ####"},
               {"city": "Haarlem", "area": "North Holland", "postcode": "201# XX", "phone": "023 ### ####"},
               {"city": "Rotterdam", "area": "South Holland", "postcode": "301# XX", "phone": "010 ### ####"},
               {"city": "The Hague", "area": "South Holland", "postcode": "251# XX", "phone": "070 ### ####"},
               {"city": "Leiden", "area": "South Holland", "postcode": "231# XX", "phone": "071 ### ####"},
               {"city": "Delft", "area": "South Holland", "postcode": "261# XX", "phone": "015 ### ####"},
               {"city": "Utrecht", "area": "Utrecht", "postcode": "351# XX", "phone": "030 ### ####"},
               {"city": "Eindhoven", "area": "North Brabant", "postcode": "561# XX", "phone": "040 ### ####"},
               {"city": "Tilburg", "area": "North Brabant", "postcode": "501# XX", "phone": "013 ### ####"},
               {"city": "Groningen", "area": "Groningen", "postcode": "971# XX", "phone": "050 ### ####"},
               {"city": "Nijmegen", "area": "Gelderland", "postcode": "652# XX", "phone": "024 ### ####"},
               {"city": "Arnhem", "area": "Gelderland", "postcode": "681# XX", "phone": "026 ### ####"},
               {"city": "Maastricht", "area": "Limburg", "postcode": "621# XX", "phone": "043 ### ####"},
               {"city": "Zwolle", "area": "Overijssel", "postcode": "801# XX", "phone": "038 ### ####"}]},
    "DK": {"name": "Denmark", "region": "EU", "currency": "DKK", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["33 ## ## ##", "+45 33 ## ## ##", "86 ## ## ##", "+45 ## ## ## ##"],
           "postcode_fmt": ["####"],
           "cities": [
               {"city": "Copenhagen", "area": "Capital Region of Denmark", "postcode": "1###", "phone": "33 ## ## ##"},
               {"city": "Aarhus", "area": "Central Denmark Region", "postcode": "8000", "phone": "86 ## ## ##"},
               {"city": "Horsens", "area": "Central Denmark Region", "postcode": "8700", "phone": "75 6# ## ##"},
               {"city": "Odense", "area": "Region of Southern Denmark", "postcode": "5000", "phone": "66 ## ## ##"},
               {"city": "Esbjerg", "area": "Region of Southern Denmark", "postcode": "6700", "phone": "75 1# ## ##"},
               {"city": "Kolding", "area": "Region of Southern Denmark", "postcode": "6000", "phone": "75 5# ## ##"},
               {"city": "Aalborg", "area": "North Denmark Region", "postcode": "9000", "phone": "98 ## ## ##"},
               {"city": "Roskilde", "area": "Region Zealand", "postcode": "4000", "phone": "46 ## ## ##"},
               {"city": "Vejle", "area": "Region of Southern Denmark", "postcode": "7100", "phone": "75 8# ## ##"}]},
}

STREETS = {
    "NL": ["Kerkstraat", "Molenweg", "Dorpsstraat", "Lindenlaan", "Schoolstraat", "Beukenlaan", "Wilhelminastraat",
           "Julianalaan", "Stationsweg", "Kastanjelaan", "Havenstraat", "Eikenlaan", "Zandstraat", "Tulpstraat",
           "Akkerweg", "Vlinderweg", "De Brink"],
    "DK": ["Kirkevej", "Skolevej", "Møllevej", "Lindevej", "Stationsvej", "Bøgevej", "Engvej", "Havnegade",
           "Strandvej", "Vestergade", "Nørregade", "Kastanievej", "Birkevej", "Skovvej", "Søndergade", "Ahornvej",
           "Torvet"]}

VENUES = {
    "NL": ["Buurthuis De Lindeboom", "Overdekte markt Zuidhaven", "Winkelcentrum Kastanjehof", "Bibliotheek Eikenhof",
           "Collegezaal 2, Gebouw Noord", "Dorpshuis De Brink", "Ontmoetingscentrum Het Akkerhuis",
           "Studentencentrum De Vlinder", "Wijkcentrum Molenkwartier"],
    "DK": ["Medborgerhuset Lindely", "Kulturhuset Møllegården", "Bøgely Markedshal", "Bibliotek Engparken",
           "Auditorium Nord, Campus Skovbakken", "Butikscenter Strandparken", "Forsamlingshuset Birkely",
           "Seniorhuset Kastanjen", "Sognegården Havnely"]}

EN_CONTEXT = {
    "NL": ["poster on the {city} university campus, where many programmes are taught in English",
           "flyer at an international school in {city}",
           "notice for the English-speaking expat and knowledge-worker community in {city}",
           "English edition of a supermarket app promotion shown in {city}",
           "staff-restaurant poster on a tech company campus in {city}",
           "advert at the railway station or airport serving {city}"],
    "DK": ["poster on the {city} university campus for international students",
           "flyer at an international school in {city}",
           "notice for newcomers at the international citizen service desk in {city}",
           "English-language advert at a supermarket near the cruise terminal or old town in {city}",
           "English edition of a food delivery app banner in {city}"]}
