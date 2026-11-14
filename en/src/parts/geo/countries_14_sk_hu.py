# Slovakia and Hungary.
COUNTRIES = {
    "SK": {"name": "Slovakia", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+421 2 #### ####", "02 #### ####", "+421 9## ### ###", "09## ### ###"],
           "postcode_fmt": ["### ##"],
           "cities": [{"city": "Bratislava", "area": "Bratislava Region", "postcode": "811 0#", "phone": "02 #### ####"},
                      {"city": "Košice", "area": "Košice Region", "postcode": "040 01", "phone": "055 ### ####"},
                      {"city": "Prešov", "area": "Prešov Region", "postcode": "080 01", "phone": "051 ### ####"},
                      {"city": "Žilina", "area": "Žilina Region", "postcode": "010 01", "phone": "041 ### ####"},
                      {"city": "Nitra", "area": "Nitra Region", "postcode": "949 01", "phone": "037 ### ####"},
                      {"city": "Banská Bystrica", "area": "Banská Bystrica Region", "postcode": "974 01", "phone": "048 ### ####"},
                      {"city": "Trnava", "area": "Trnava Region", "postcode": "917 01", "phone": "033 ### ####"},
                      {"city": "Trenčín", "area": "Trenčín Region", "postcode": "911 01", "phone": "032 ### ####"}]},
    "HU": {"name": "Hungary", "region": "EU", "currency": "HUF", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+36 1 ### ####", "06 1 ### ####", "+36 30 ### ####", "+36 20 ### ####", "+36 52 ### ###"],
           "postcode_fmt": ["####"],
           "cities": [{"city": "Budapest", "area": "Budapest", "postcode": "1###", "phone": "+36 1 ### ####"},
                      {"city": "Debrecen", "area": "Hajdú-Bihar County", "postcode": "402#", "phone": "+36 52 ### ###"},
                      {"city": "Szeged", "area": "Csongrád-Csanád County", "postcode": "672#", "phone": "+36 62 ### ###"},
                      {"city": "Pécs", "area": "Baranya County", "postcode": "762#", "phone": "+36 72 ### ###"},
                      {"city": "Győr", "area": "Győr-Moson-Sopron County", "postcode": "902#", "phone": "+36 96 ### ###"},
                      {"city": "Miskolc", "area": "Borsod-Abaúj-Zemplén County", "postcode": "352#", "phone": "+36 46 ### ###"},
                      {"city": "Székesfehérvár", "area": "Fejér County", "postcode": "800#", "phone": "+36 22 ### ###"},
                      {"city": "Eger", "area": "Heves County", "postcode": "3300", "phone": "+36 36 ### ###"}]},
}

STREETS = {
    "SK": ["Školská", "Hlavná", "Lipová", "Záhradná", "Krátka", "Poľná", "Kostolná", "Lúčna", "Mlynská", "Štúrova",
           "Hviezdoslavova", "Nová", "Lesná", "Sadová", "Jarná", "Orgovánová", "Družstevná"],
    "HU": ["Petőfi Sándor utca", "Kossuth Lajos utca", "Fő utca", "Rákóczi út", "Ady Endre utca", "Templom utca",
           "Iskola utca", "Malom utca", "Hársfa utca", "Kert utca", "Rózsa utca", "Béke utca", "Jókai Mór utca",
           "Arany János utca", "Vasút utca", "Széchenyi tér", "Diófa utca"]}

VENUES = {
    "SK": ["Komunitné centrum Lipka", "Kultúrny dom Pod Lipami", "Tržnica Pri Mlyne", "Knižnica Sadová",
           "Aula kampusu Lúčna", "Obchodné centrum Záhrada", "Farská sála sv. Martina", "Klub seniorov Jarná",
           "Športová hala Orgován"],
    "HU": ["Hársfa Közösségi Ház", "Malomkert Művelődési Központ", "Diófa Vásárcsarnok", "Rózsakert Könyvtár",
           "Kampusz Aula, Kert utca", "Napfény Bevásárlóközpont", "Szent István Plébániaterem",
           "Béke Nyugdíjasklub", "Fűzfa Sportcsarnok"]}

EN_CONTEXT = {
    "SK": ["poster on the {city} university campus for Erasmus students",
           "staff-kitchen poster at an international automotive plant near {city}",
           "flyer at an international school in {city}",
           "notice for the English-speaking expat community in {city}",
           "advert in the tourist old town of {city}"],
    "HU": ["poster on the {city} university campus for international medical students",
           "advert in the tourist centre of {city}",
           "staff-kitchen poster at a multinational shared-services office in {city}",
           "flyer at an international school in {city}",
           "food-court advert at {city} airport or main railway station"]}
