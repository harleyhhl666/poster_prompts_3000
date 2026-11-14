# Slovenia and Croatia.
COUNTRIES = {
    "SI": {"name": "Slovenia", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+386 1 ### ## ##", "01 ### ## ##", "+386 2 ### ## ##", "+386 41 ### ###", "040 ### ###"],
           "postcode_fmt": ["####"],
           "cities": [{"city": "Ljubljana", "area": "Central Slovenia", "postcode": "10##", "phone": "01 ### ## ##"},
                      {"city": "Maribor", "area": "Drava", "postcode": "2000", "phone": "02 ### ## ##"},
                      {"city": "Celje", "area": "Savinja", "postcode": "3000", "phone": "03 ### ## ##"},
                      {"city": "Kranj", "area": "Upper Carniola", "postcode": "4000", "phone": "04 ### ## ##"},
                      {"city": "Koper", "area": "Coastal–Karst", "postcode": "6000", "phone": "05 ### ## ##"},
                      {"city": "Novo Mesto", "area": "Southeast Slovenia", "postcode": "8000", "phone": "07 ### ## ##"},
                      {"city": "Nova Gorica", "area": "Gorizia", "postcode": "5000", "phone": "05 ### ## ##"}]},
    "HR": {"name": "Croatia", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["+385 1 ### ####", "01 ### ####", "+385 21 ### ###", "+385 91 ### ####", "098 ### ####"],
           "postcode_fmt": ["#####"],
           "cities": [{"city": "Zagreb", "area": "City of Zagreb", "postcode": "100#0", "phone": "01 ### ####"},
                      {"city": "Split", "area": "Split-Dalmatia County", "postcode": "21000", "phone": "021 ### ###"},
                      {"city": "Rijeka", "area": "Primorje-Gorski Kotar County", "postcode": "51000", "phone": "051 ### ###"},
                      {"city": "Osijek", "area": "Osijek-Baranja County", "postcode": "31000", "phone": "031 ### ###"},
                      {"city": "Zadar", "area": "Zadar County", "postcode": "23000", "phone": "023 ### ###"},
                      {"city": "Pula", "area": "Istria County", "postcode": "52100", "phone": "052 ### ###"},
                      {"city": "Dubrovnik", "area": "Dubrovnik-Neretva County", "postcode": "20000", "phone": "020 ### ###"},
                      {"city": "Varaždin", "area": "Varaždin County", "postcode": "42000", "phone": "042 ### ###"}]},
}

STREETS = {
    "SI": ["Šolska ulica", "Cankarjeva cesta", "Prešernova ulica", "Lipova ulica", "Vrtna ulica", "Cerkvena ulica",
           "Mlinska ulica", "Kratka ulica", "Gozdna pot", "Trubarjeva ulica", "Sončna ulica", "Kolodvorska ulica",
           "Partizanska cesta", "Cvetlična ulica", "Ulica pod gozdom", "Brezova ulica", "Travniška ulica"],
    "HR": ["Ulica Ivana Gundulića", "Školska ulica", "Vukovarska ulica", "Ulica kralja Tomislava", "Lipova ulica",
           "Vrtna ulica", "Crkvena ulica", "Mlinska ulica", "Kratka ulica", "Primorska ulica", "Ulica Matije Gupca",
           "Obala hrvatskih branitelja", "Ulica Stjepana Radića", "Cvjetna ulica", "Kolodvorska ulica",
           "Maslinova ulica", "Šetalište uz more"]}

VENUES = {
    "SI": ["Skupnostni center Lipa", "Kulturni dom Pod Lipami", "Tržnica Pri mlinu", "Knjižnica Brezova",
           "Avla kampusa Travnik", "Nakupovalno središče Sončni vrt", "Župnijska dvorana sv. Jakoba",
           "Klub upokojencev Cvetlica", "Športna dvorana Gozdna pot"],
    "HR": ["Društveni dom Maslina", "Kulturni centar Pod Lipom", "Tržnica Kod mlina", "Gradska knjižnica Cvjetna",
           "Aula kampusa Lungomare", "Trgovački centar Sunčani vrt", "Župna dvorana sv. Duje",
           "Klub umirovljenika Lavanda", "Sportska dvorana Borik"]}

EN_CONTEXT = {
    "SI": ["poster on the {city} university campus for Erasmus students",
           "advert in the tourist old town of {city}",
           "flyer at an international school in {city}",
           "notice for the English-speaking expat community in {city}",
           "staff-kitchen poster at an international pharmaceutical company in {city}"],
    "HR": ["advert for summer tourists along the {city} waterfront",
           "menu-board poster at a beach café in {city} serving foreign visitors",
           "poster on the {city} university campus for international students",
           "notice for digital nomads at a co-working space in {city}",
           "food-court advert at {city} airport or ferry terminal"]}
