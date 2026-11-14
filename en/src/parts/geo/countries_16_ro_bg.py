# Romania and Bulgaria (Bulgaria uses the euro from 1 Jan 2026).
COUNTRIES = {
    "RO": {"name": "Romania", "region": "EU", "currency": "RON", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+40 21 ### ####", "021 ### ####", "+40 264 ### ###", "+40 7## ### ###", "07## ### ###"],
           "postcode_fmt": ["######"],
           "cities": [{"city": "Bucharest", "area": "Bucharest", "postcode": "03####", "phone": "021 ### ####"},
                      {"city": "Cluj-Napoca", "area": "Cluj County", "postcode": "400###", "phone": "0264 ### ###"},
                      {"city": "Timișoara", "area": "Timiș County", "postcode": "300###", "phone": "0256 ### ###"},
                      {"city": "Iași", "area": "Iași County", "postcode": "700###", "phone": "0232 ### ###"},
                      {"city": "Brașov", "area": "Brașov County", "postcode": "500###", "phone": "0268 ### ###"},
                      {"city": "Constanța", "area": "Constanța County", "postcode": "900###", "phone": "0241 ### ###"},
                      {"city": "Sibiu", "area": "Sibiu County", "postcode": "550###", "phone": "0269 ### ###"},
                      {"city": "Oradea", "area": "Bihor County", "postcode": "410###", "phone": "0259 ### ###"}]},
    "BG": {"name": "Bulgaria", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+359 2 ### ####", "02 ### ####", "+359 52 ### ###", "+359 88# ### ###", "089 ### ####"],
           "postcode_fmt": ["####"],
           "cities": [{"city": "Sofia", "area": "Sofia City Province", "postcode": "10##", "phone": "02 ### ####"},
                      {"city": "Plovdiv", "area": "Plovdiv Province", "postcode": "400#", "phone": "032 ### ###"},
                      {"city": "Varna", "area": "Varna Province", "postcode": "900#", "phone": "052 ### ###"},
                      {"city": "Burgas", "area": "Burgas Province", "postcode": "800#", "phone": "056 ### ###"},
                      {"city": "Ruse", "area": "Ruse Province", "postcode": "700#", "phone": "082 ### ###"},
                      {"city": "Stara Zagora", "area": "Stara Zagora Province", "postcode": "600#", "phone": "042 ### ###"},
                      {"city": "Veliko Tarnovo", "area": "Veliko Tarnovo Province", "postcode": "500#", "phone": "062 ### ###"}]},
}

STREETS = {
    "RO": ["Strada Școlii", "Strada Teilor", "Strada Morii", "Strada Bisericii", "Strada Florilor", "Strada Grădinilor",
           "Strada Mihai Eminescu", "Bulevardul Unirii", "Strada Libertății", "Strada Primăverii", "Strada Gării",
           "Strada Nucilor", "Strada Ion Creangă", "Strada Câmpului", "Strada Pădurii", "Strada Viilor",
           "Strada Liliacului"],
    "BG": ["ul. Vasil Levski", "ul. Hristo Botev", "ul. Rakovski", "bul. Tsar Osvoboditel", "ul. Lipa", "ul. Rozova",
           "ul. Cherkovna", "ul. Melnichna", "ul. Gradinska", "ul. Ivan Vazov", "ul. Slaveykov", "ul. Shipka",
           "ul. Orehova", "ul. Pirin", "ul. Lozarska", "ul. Kestenova", "ul. Ribarska"]}

VENUES = {
    "RO": ["Centrul Comunitar Teiul", "Casa de Cultură Grădina Veche", "Piața Agroalimentară La Moară",
           "Biblioteca de Cartier Nucilor", "Aula Campusului Primăverii", "Centrul Comercial Valea Florilor",
           "Sala Parohială Sf. Nicolae", "Clubul Pensionarilor Liliacul", "Sala Sporturilor Pădurea Verde"],
    "BG": ["Chitalishte Lipa", "Obshtnosten Tsentar Rozova Gradina", "Pazar Melnitsata", "Biblioteka Kestenova",
           "Aula Kampus Pirin", "Targovski Tsentar Slanchev Dvor", "Enorijska Zala Sv. Georgi",
           "Klub na Pensionera Lozata", "Sportna Zala Orehite"]}

EN_CONTEXT = {
    "RO": ["staff-kitchen poster at an international IT outsourcing office in {city}",
           "poster on the {city} university campus for international medical students",
           "flyer at an international school in {city}",
           "advert in the tourist old town of {city}",
           "notice for the English-speaking expat community in {city}"],
    "BG": ["advert for summer tourists at a beach resort near {city}",
           "staff-kitchen poster at a multinational tech office in {city}",
           "poster on the {city} university campus for international medical students",
           "notice for the British retiree community near {city}",
           "food-court advert at {city} airport"]}
