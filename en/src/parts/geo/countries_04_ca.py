# Canada (English-speaking provinces only; no Quebec). 555-0100..0199 fictional range; real area codes.
def _c(city, prov, pc, ac):
    return {"city": city, "area": prov, "postcode": pc, "phone": "(%s) 555-01##" % ac}


COUNTRIES = {"CA": {
    "name": "Canada", "region": "CA", "currency": "CAD", "lang_context": "native", "date_style": "us",
    "phone_fmt": ["(416) 555-01##", "(613) 555-01##", "(604) 555-01##", "(403) 555-01##", "(902) 555-01##",
                  "1-800-555-01##"],
    "postcode_fmt": ["X#X #X#"],
    "cities": [
        _c("Toronto", "ON", "M5V #K#", "416"), _c("Ottawa", "ON", "K1P #B#", "613"),
        _c("Hamilton", "ON", "L8P #T#", "905"), _c("London", "ON", "N6A #M#", "519"),
        _c("Kingston", "ON", "K7L #R#", "613"), _c("Waterloo", "ON", "N2L #G#", "519"),
        _c("Thunder Bay", "ON", "P7B #E#", "807"), _c("Vancouver", "BC", "V6B #H#", "604"),
        _c("Victoria", "BC", "V8W #C#", "250"), _c("Kelowna", "BC", "V1Y #N#", "250"),
        _c("Calgary", "AB", "T2P #S#", "403"), _c("Edmonton", "AB", "T5J #A#", "780"),
        _c("Lethbridge", "AB", "T1J #W#", "403"), _c("Winnipeg", "MB", "R3C #L#", "204"),
        _c("Saskatoon", "SK", "S7K #P#", "306"), _c("Regina", "SK", "S4P #J#", "306"),
        _c("Halifax", "NS", "B3H #V#", "902"), _c("St. John's", "NL", "A1C #E#", "709"),
        _c("Fredericton", "NB", "E3B #K#", "506"), _c("Moncton", "NB", "E1C #T#", "506"),
        _c("Charlottetown", "PE", "C1A #N#", "902"),
    ]}}

STREETS = {"CA": [
    "Maple Avenue", "King Street", "Queen Street", "Lakeshore Road", "Birch Crescent", "Pine Ridge Drive",
    "Victoria Street", "Spruce Lane", "Wellington Street", "Church Street", "Harbourview Road", "Elm Grove",
    "Prairie View Drive", "Cedar Point Road", "Riverside Drive", "Aspen Way", "Brock Street", "Main Street",
    "Mountain View Road", "Poplar Avenue"]}

VENUES = {"CA": [
    "Birchwood Community Centre", "Lakeshore Branch Library", "Harbourview Farmers' Market Hall",
    "Prairie Gate Shopping Centre", "St. Columba's Church Hall", "Aspen Grove Seniors' Centre",
    "Room 210, MacLeod Hall", "Spruce Lane Legion Hall", "Riverside Curling Club Lounge",
    "Pine Ridge Recreation Complex", "Wellington Square Atrium", "Mountain View Community League Hall"]}
