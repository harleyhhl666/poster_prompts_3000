# Estonia, Latvia, Lithuania.
_I = {"region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu"}
COUNTRIES = {
    "EE": dict(_I, name="Estonia", phone_fmt=["+372 6## ####", "6## ####", "+372 7## ####", "+372 5### ####"],
               postcode_fmt=["#####"],
               cities=[{"city": "Tallinn", "area": "Harju County", "postcode": "1####", "phone": "+372 6## ####"},
                       {"city": "Tartu", "area": "Tartu County", "postcode": "50###", "phone": "+372 74# ####"},
                       {"city": "Pärnu", "area": "Pärnu County", "postcode": "80###", "phone": "+372 44# ####"},
                       {"city": "Narva", "area": "Ida-Viru County", "postcode": "20###", "phone": "+372 35# ####"},
                       {"city": "Viljandi", "area": "Viljandi County", "postcode": "710##", "phone": "+372 43# ####"},
                       {"city": "Rakvere", "area": "Lääne-Viru County", "postcode": "443##", "phone": "+372 32# ####"}]),
    "LV": dict(_I, name="Latvia", phone_fmt=["+371 67 ### ###", "67 ### ###", "+371 2# ### ###", "2# ### ###"],
               postcode_fmt=["LV-####"],
               cities=[{"city": "Riga", "area": "Riga", "postcode": "LV-10##", "phone": "+371 67 ### ###"},
                       {"city": "Daugavpils", "area": "Latgale", "postcode": "LV-54##", "phone": "+371 65 4## ###"},
                       {"city": "Liepāja", "area": "Courland", "postcode": "LV-34##", "phone": "+371 63 4## ###"},
                       {"city": "Jelgava", "area": "Semigallia", "postcode": "LV-30##", "phone": "+371 63 0## ###"},
                       {"city": "Jūrmala", "area": "Riga Planning Region", "postcode": "LV-201#", "phone": "+371 67 7## ###"},
                       {"city": "Valmiera", "area": "Vidzeme", "postcode": "LV-420#", "phone": "+371 64 2## ###"}]),
    "LT": dict(_I, name="Lithuania", phone_fmt=["+370 5 ### ####", "(8 5) ### ####", "+370 37 ######",
                                                 "+370 6## #####", "86## #####"],
               postcode_fmt=["LT-#####"],
               cities=[{"city": "Vilnius", "area": "Vilnius County", "postcode": "LT-0####", "phone": "(8 5) ### ####"},
                       {"city": "Kaunas", "area": "Kaunas County", "postcode": "LT-44###", "phone": "(8 37) ######"},
                       {"city": "Klaipėda", "area": "Klaipėda County", "postcode": "LT-92###", "phone": "(8 46) ######"},
                       {"city": "Šiauliai", "area": "Šiauliai County", "postcode": "LT-76###", "phone": "(8 41) ######"},
                       {"city": "Panevėžys", "area": "Panevėžys County", "postcode": "LT-35###", "phone": "(8 45) ######"},
                       {"city": "Alytus", "area": "Alytus County", "postcode": "LT-62###", "phone": "(8 315) #####"}]),
}

STREETS = {
    "EE": ["Kooli tänav", "Pärna tänav", "Aia tänav", "Kiriku tänav", "Veski tänav", "Metsa tänav", "Lille tänav",
           "Jaama tänav", "Pikk tänav", "Lühike tänav", "Mere puiestee", "Kase tänav", "Vahtra tänav", "Tamme tänav",
           "Õuna tänav", "Karja tänav", "Rahu tänav"],
    "LV": ["Skolas iela", "Liepu iela", "Dārza iela", "Baznīcas iela", "Dzirnavu iela", "Meža iela", "Ziedu iela",
           "Stacijas iela", "Brīvības iela", "Īsā iela", "Bērzu iela", "Kļavu iela", "Ozolu iela", "Ābeļu iela",
           "Jūras iela", "Krasta iela", "Saules iela"],
    "LT": ["Mokyklos g.", "Liepų g.", "Sodų g.", "Bažnyčios g.", "Malūno g.", "Miško g.", "Gėlių g.", "Stoties g.",
           "Laisvės al.", "Trumpoji g.", "Beržų g.", "Klevų g.", "Ąžuolų g.", "Obelų g.", "Saulės g.", "Vytauto g.",
           "Pievų g."]}

VENUES = {
    "EE": ["Pärnaaia Kogukonnamaja", "Veskimäe Kultuurikeskus", "Kaseoru Turuhoone", "Lillemäe Raamatukogu",
           "Tammiku Ülikoolilinnaku Aula", "Õunapuu Kaubanduskeskus", "Püha Jaani Kogudusemaja",
           "Vahtra Eakate Klubi", "Mereranna Spordihall"],
    "LV": ["Liepkalna Kopienas nams", "Dzirnavu Kultūras centrs", "Bērzu Tirgus halle", "Ziedkalnes bibliotēka",
           "Ozolu Kampusa aula", "Saulgriežu Tirdzniecības centrs", "Sv. Jāņa draudzes zāle",
           "Kļavu Senioru klubs", "Jūrmalas Krasta sporta halle"],
    "LT": ["Liepų Bendruomenės namai", "Malūno Kultūros centras", "Beržyno Turgaus halė", "Sodų Biblioteka",
           "Ąžuolyno Miestelio aula", "Saulėtekio Prekybos centras", "Šv. Jono Parapijos salė",
           "Klevų Senjorų klubas", "Pievų Sporto arena"]}

_R = ["poster on the {city} university campus for international students",
      "staff-kitchen poster at an international tech start-up office in {city}",
      "flyer at an international school in {city}",
      "advert in the tourist old town of {city}",
      "notice for the English-speaking expat community in {city}"]
EN_CONTEXT = {"EE": _R + ["English edition of a grocery delivery app banner shown in {city}"],
              "LV": _R + ["food-court advert at {city} airport or central station"],
              "LT": _R + ["poster at a shared-services centre canteen in {city}"]}
