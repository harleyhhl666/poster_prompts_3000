# Spain and Portugal.
COUNTRIES = {
    "ES": {"name": "Spain", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["91# ### ###", "+34 91# ### ###", "+34 93# ### ###", "95# ### ###", "6## ### ###"],
           "postcode_fmt": ["#####"],
           "cities": [
               {"city": "Madrid", "area": "Community of Madrid", "postcode": "2801#", "phone": "91# ### ###"},
               {"city": "Barcelona", "area": "Catalonia", "postcode": "080##", "phone": "93# ### ###"},
               {"city": "Girona", "area": "Catalonia", "postcode": "1700#", "phone": "972 ### ###"},
               {"city": "Valencia", "area": "Valencian Community", "postcode": "460##", "phone": "96# ### ###"},
               {"city": "Alicante", "area": "Valencian Community", "postcode": "030##", "phone": "965 ### ###"},
               {"city": "Seville", "area": "Andalusia", "postcode": "410##", "phone": "954 ### ###"},
               {"city": "Málaga", "area": "Andalusia", "postcode": "290##", "phone": "952 ### ###"},
               {"city": "Granada", "area": "Andalusia", "postcode": "180##", "phone": "958 ### ###"},
               {"city": "Bilbao", "area": "Basque Country", "postcode": "480##", "phone": "944 ### ###"},
               {"city": "Zaragoza", "area": "Aragon", "postcode": "500##", "phone": "976 ### ###"},
               {"city": "Palma", "area": "Balearic Islands", "postcode": "070##", "phone": "971 ### ###"},
               {"city": "Salamanca", "area": "Castile and León", "postcode": "370##", "phone": "923 ### ###"},
               {"city": "Santander", "area": "Cantabria", "postcode": "390##", "phone": "942 ### ###"},
               {"city": "Las Palmas de Gran Canaria", "area": "Canary Islands", "postcode": "350##", "phone": "928 ### ###"}]},
    "PT": {"name": "Portugal", "region": "EU", "currency": "EUR", "lang_context": "international", "date_style": "eu",
           "phone_fmt": ["21# ### ###", "+351 21# ### ###", "+351 22# ### ###", "289 ### ###", "+351 91# ### ###"],
           "postcode_fmt": ["####-###"],
           "cities": [
               {"city": "Lisbon", "area": "Lisbon District", "postcode": "1###-###", "phone": "21# ### ###"},
               {"city": "Cascais", "area": "Lisbon District", "postcode": "2750-###", "phone": "214 ### ###"},
               {"city": "Porto", "area": "Porto District", "postcode": "4050-###", "phone": "22# ### ###"},
               {"city": "Braga", "area": "Braga District", "postcode": "4700-###", "phone": "253 ### ###"},
               {"city": "Coimbra", "area": "Coimbra District", "postcode": "3000-###", "phone": "239 ### ###"},
               {"city": "Aveiro", "area": "Aveiro District", "postcode": "3800-###", "phone": "234 ### ###"},
               {"city": "Faro", "area": "Faro District (Algarve)", "postcode": "8000-###", "phone": "289 ### ###"},
               {"city": "Lagos", "area": "Faro District (Algarve)", "postcode": "8600-###", "phone": "282 ### ###"},
               {"city": "Évora", "area": "Évora District", "postcode": "7000-###", "phone": "266 ### ###"},
               {"city": "Setúbal", "area": "Setúbal District", "postcode": "2900-###", "phone": "265 ### ###"},
               {"city": "Funchal", "area": "Madeira", "postcode": "9000-###", "phone": "291 ### ###"}]},
}

STREETS = {
    "ES": ["Calle Mayor", "Calle de la Iglesia", "Calle del Molino", "Calle de los Olivos", "Calle Real",
           "Avenida de la Constitución", "Calle de las Flores", "Calle del Sol", "Plaza de la Fuente", "Calle San José",
           "Calle de la Estación", "Calle Nueva", "Calle del Carmen", "Calle de los Almendros", "Calle de la Huerta"],
    "PT": ["Rua da Igreja", "Rua do Moinho", "Rua das Flores", "Rua Nova", "Rua da Escola", "Rua do Sol",
           "Travessa do Poço", "Rua dos Pinheiros", "Largo do Chafariz", "Rua da Fonte", "Rua das Oliveiras",
           "Rua de São João", "Rua do Mercado", "Rua da Estação", "Rua dos Lírios", "Avenida 25 de Abril"]}

VENUES = {
    "ES": ["Centro Cívico Los Almendros", "Mercado Municipal de la Huerta", "Biblioteca Pública Barrio del Sol",
           "Aula Magna, Campus de los Olivos", "Centro Comercial Puerta del Molino", "Salón Parroquial San José",
           "Hogar del Jubilado La Fuente", "Casal de Barri del Mar", "Centro Sociocultural El Carmen"],
    "PT": ["Centro Comunitário das Oliveiras", "Mercado Municipal do Chafariz", "Biblioteca Municipal dos Pinheiros",
           "Auditório B, Campus do Moinho", "Centro Comercial Jardim dos Lírios", "Salão Paroquial de São João",
           "Associação de Moradores do Poço", "Casa do Povo da Fonte", "Pavilhão Multiusos da Estação"]}

EN_CONTEXT = {
    "ES": ["English-language poster for British and Irish residents on the coast near {city}",
           "flyer at an international school in {city}",
           "poster on the {city} university campus for Erasmus students",
           "advert in the tourist old town of {city} aimed at English-speaking visitors",
           "English-language shelf poster at an international supermarket in {city}",
           "food-court advert at {city} airport"],
    "PT": ["poster for the English-speaking expat and digital-nomad community in {city}",
           "flyer at an international school in {city}",
           "advert in the historic centre of {city} aimed at tourists",
           "English edition of a grocery delivery app banner shown in {city}",
           "poster on the {city} university campus for international students"]}
