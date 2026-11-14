# Finland and Iceland.
COUNTRIES = {
    "FI": {"name": "Finland", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["09 ### ####", "+358 9 ### ####", "03 ### ####", "040 ### ####", "+358 50 ### ####"],
           "postcode_fmt": ["#####"],
           "cities": [{"city": "Helsinki", "area": "Uusimaa", "postcode": "001#0", "phone": "09 ### ####"},
                      {"city": "Espoo", "area": "Uusimaa", "postcode": "021#0", "phone": "09 ### ####"},
                      {"city": "Tampere", "area": "Pirkanmaa", "postcode": "331#0", "phone": "03 ### ####"},
                      {"city": "Turku", "area": "Southwest Finland", "postcode": "20#00", "phone": "02 ### ####"},
                      {"city": "Oulu", "area": "North Ostrobothnia", "postcode": "90#00", "phone": "08 ### ####"},
                      {"city": "Jyväskylä", "area": "Central Finland", "postcode": "40#00", "phone": "014 ### ####"},
                      {"city": "Kuopio", "area": "North Savo", "postcode": "70#00", "phone": "017 ### ####"},
                      {"city": "Lahti", "area": "Päijät-Häme", "postcode": "15#00", "phone": "03 ### ####"},
                      {"city": "Vaasa", "area": "Ostrobothnia", "postcode": "651#0", "phone": "06 ### ####"},
                      {"city": "Rovaniemi", "area": "Lapland", "postcode": "96#00", "phone": "016 ### ####"}]},
    "IS": {"name": "Iceland", "region": "EU", "currency": "ISK", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["5## ####", "+354 5## ####", "4## ####", "+354 8## ####"],
           "postcode_fmt": ["###"],
           "cities": [{"city": "Reykjavík", "area": "Capital Region", "postcode": "10#", "phone": "+354 5## ####"},
                      {"city": "Kópavogur", "area": "Capital Region", "postcode": "200", "phone": "+354 5## ####"},
                      {"city": "Hafnarfjörður", "area": "Capital Region", "postcode": "220", "phone": "+354 5## ####"},
                      {"city": "Garðabær", "area": "Capital Region", "postcode": "210", "phone": "+354 5## ####"},
                      {"city": "Akureyri", "area": "Northeast Region", "postcode": "600", "phone": "+354 46# ####"},
                      {"city": "Reykjanesbær", "area": "Southern Peninsula", "postcode": "230", "phone": "+354 42# ####"},
                      {"city": "Selfoss", "area": "South Region", "postcode": "800", "phone": "+354 48# ####"},
                      {"city": "Ísafjörður", "area": "Westfjords", "postcode": "400", "phone": "+354 45# ####"},
                      {"city": "Egilsstaðir", "area": "East Region", "postcode": "700", "phone": "+354 47# ####"},
                      {"city": "Akranes", "area": "West Region", "postcode": "300", "phone": "+354 43# ####"}]},
}

STREETS = {
    "FI": ["Koulukatu", "Kirkkokatu", "Asemakatu", "Myllytie", "Koivutie", "Rantatie", "Puistokatu", "Kauppakatu",
           "Pihlajatie", "Mäntytie", "Kuusitie", "Harjukatu", "Satamakatu", "Torikatu", "Lehtotie", "Niittytie"],
    "IS": ["Kirkjuvegur", "Skólavegur", "Hafnargata", "Aðalgata", "Bakkavegur", "Birkihlíð", "Melgerði",
           "Sólvallagata", "Túngata", "Grundarstígur", "Strandgata", "Holtsgata", "Hlíðarvegur", "Heiðarvegur",
           "Lækjarvegur", "Lindargata"]}

VENUES = {
    "FI": ["Asukastalo Koivula", "Kauppahalli Rantala", "Kulttuuritalo Pihlaja", "Kirjasto Mäntylä",
           "Luentosali 2, Kampus Harju", "Kauppakeskus Lehtola", "Seurakuntatalo Kuusikko", "Palvelukeskus Myllytupa",
           "Nuorisotalo Niittyranta"],
    "IS": ["Félagsheimilið Birkihlíð", "Bókasafn Melgerðis", "Matarmarkaðurinn við Höfnina", "Íþróttahúsið Holt",
           "Safnaðarheimilið Hlíð", "Menningarhúsið Strönd", "Fyrirlestrasalur Grund, háskólasvæði",
           "Verslunarmiðstöðin Heiði", "Samkomuhúsið Bakki"]}

EN_CONTEXT = {
    "FI": ["poster on the {city} university campus for international degree students",
           "flyer at an international school in {city}",
           "notice for the English-speaking tech and research community in {city}",
           "English edition of a grocery delivery app banner shown in {city}",
           "advert for winter tourists near the travel centre in {city}"],
    "IS": ["poster at a tourist information centre in {city}",
           "English-language advert at a supermarket popular with visitors in {city}",
           "notice for the international workers' community in {city}",
           "poster in a guesthouse breakfast room in {city}",
           "advert at the airport or bus terminal serving {city}"]}
