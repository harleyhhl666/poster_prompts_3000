# Sweden and Norway.
COUNTRIES = {
    "SE": {"name": "Sweden", "region": "EU", "currency": "SEK", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["08-### ### ##", "+46 8 ### ### ##", "031-### ## ##", "040-### ## ##", "070-### ## ##"],
           "postcode_fmt": ["### ##"],
           "cities": [{"city": "Stockholm", "area": "Stockholm County", "postcode": "11# ##", "phone": "08-### ### ##"},
                      {"city": "Gothenburg", "area": "Västra Götaland County", "postcode": "41# ##", "phone": "031-### ## ##"},
                      {"city": "Malmö", "area": "Skåne County", "postcode": "21# ##", "phone": "040-### ## ##"},
                      {"city": "Lund", "area": "Skåne County", "postcode": "223 ##", "phone": "046-### ## ##"},
                      {"city": "Helsingborg", "area": "Skåne County", "postcode": "252 ##", "phone": "042-### ## ##"},
                      {"city": "Uppsala", "area": "Uppsala County", "postcode": "752 ##", "phone": "018-### ## ##"},
                      {"city": "Linköping", "area": "Östergötland County", "postcode": "58# ##", "phone": "013-### ## ##"},
                      {"city": "Norrköping", "area": "Östergötland County", "postcode": "602 ##", "phone": "011-### ## ##"},
                      {"city": "Örebro", "area": "Örebro County", "postcode": "702 ##", "phone": "019-### ## ##"},
                      {"city": "Västerås", "area": "Västmanland County", "postcode": "722 ##", "phone": "021-### ## ##"},
                      {"city": "Umeå", "area": "Västerbotten County", "postcode": "903 ##", "phone": "090-### ## ##"}]},
    "NO": {"name": "Norway", "region": "EU", "currency": "NOK", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["22 ## ## ##", "+47 22 ## ## ##", "55 ## ## ##", "+47 4## ## ###", "9## ## ###"],
           "postcode_fmt": ["####"],
           "cities": [{"city": "Oslo", "area": "Oslo", "postcode": "0###", "phone": "22 ## ## ##"},
                      {"city": "Bergen", "area": "Vestland", "postcode": "50##", "phone": "55 ## ## ##"},
                      {"city": "Trondheim", "area": "Trøndelag", "postcode": "70##", "phone": "73 ## ## ##"},
                      {"city": "Stavanger", "area": "Rogaland", "postcode": "40##", "phone": "51 ## ## ##"},
                      {"city": "Tromsø", "area": "Troms", "postcode": "90##", "phone": "77 ## ## ##"},
                      {"city": "Kristiansand", "area": "Agder", "postcode": "461#", "phone": "38 ## ## ##"},
                      {"city": "Drammen", "area": "Buskerud", "postcode": "301#", "phone": "32 ## ## ##"},
                      {"city": "Fredrikstad", "area": "Østfold", "postcode": "161#", "phone": "69 ## ## ##"},
                      {"city": "Ålesund", "area": "Møre og Romsdal", "postcode": "601#", "phone": "70 ## ## ##"},
                      {"city": "Bodø", "area": "Nordland", "postcode": "80##", "phone": "75 ## ## ##"}]},
}

STREETS = {
    "SE": ["Storgatan", "Kyrkogatan", "Skolgatan", "Kvarngatan", "Lindvägen", "Björkvägen", "Stationsgatan",
           "Ängsvägen", "Hamngatan", "Ekvägen", "Torggatan", "Sjövägen", "Parkgatan", "Granvägen", "Backavägen",
           "Prästgårdsgatan", "Rönnvägen"],
    "NO": ["Kirkeveien", "Skoleveien", "Storgata", "Møllebakken", "Bjørkeveien", "Lindeveien", "Stasjonsveien",
           "Havnegata", "Strandveien", "Granveien", "Fjellveien", "Bakkeveien", "Furuveien", "Skogveien",
           "Elveveien", "Solbakken", "Torggata"]}

VENUES = {
    "SE": ["Medborgarhuset Linden", "Saluhallen Kvarnbacken", "Folkets hus Ängsbacken", "Biblioteket Eklunda",
           "Aula Campus Sjöstaden", "Köpcentrum Granparken", "Församlingshemmet Kvarnbacka", "Träffpunkt Lingonet",
           "Kulturhuset Rönnen"],
    "NO": ["Kulturhuset Fjellstua", "Grendehuset Solbakken", "Bydelshuset Furulund", "Torghallen Elvebakken",
           "Biblioteket Granly", "Auditorium Lyngheia, Campus Nord", "Kjøpesenteret Havnelyset",
           "Menighetssalen Bjørkely", "Seniorsenteret Skogly"]}

EN_CONTEXT = {
    "SE": ["poster on the {city} university campus for international master's students",
           "flyer at an international school in {city}",
           "notice for the English-speaking expat and tech-worker community in {city}",
           "English edition of a grocery delivery app banner shown in {city}",
           "staff-canteen poster at a multinational company office in {city}"],
    "NO": ["poster on the {city} university campus for international students and researchers",
           "flyer at an international school in {city}",
           "notice for English-speaking energy-sector expats and families in {city}",
           "advert for cruise and hiking tourists in the harbour area of {city}",
           "airport food-court advert at {city} airport"]}
