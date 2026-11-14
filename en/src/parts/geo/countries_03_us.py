# United States: 555-0100..0199 is the reserved fictional range; city area codes are real.
def _c(city, state, zipc, ac):
    return {"city": city, "area": state, "postcode": zipc, "phone": "(%s) 555-01##" % ac}


COUNTRIES = {"US": {
    "name": "United States", "region": "US", "currency": "USD", "lang_context": "native", "date_style": "us",
    "phone_fmt": ["(614) 555-01##", "(503) 555-01##", "(512) 555-01##", "(617) 555-01##", "(206) 555-01##",
                  "(919) 555-01##", "(412) 555-01##", "(303) 555-01##", "1-800-555-01##"],
    "postcode_fmt": ["#####"],
    "cities": [
        _c("Columbus", "OH", "432##", "614"), _c("Cleveland", "OH", "441##", "216"),
        _c("Portland", "OR", "972##", "503"), _c("Eugene", "OR", "9740#", "541"),
        _c("Denver", "CO", "802##", "303"), _c("Fort Collins", "CO", "8052#", "970"),
        _c("Austin", "TX", "787##", "512"), _c("San Antonio", "TX", "782##", "210"),
        _c("Minneapolis", "MN", "554##", "612"), _c("Raleigh", "NC", "276##", "919"),
        _c("Asheville", "NC", "2880#", "828"), _c("Pittsburgh", "PA", "152##", "412"),
        _c("Madison", "WI", "537##", "608"), _c("Sacramento", "CA", "958##", "916"),
        _c("San Diego", "CA", "921##", "619"), _c("Boston", "MA", "0211#", "617"),
        _c("Worcester", "MA", "0160#", "508"), _c("Seattle", "WA", "981##", "206"),
        _c("Spokane", "WA", "992##", "509"), _c("Atlanta", "GA", "303##", "404"),
        _c("Savannah", "GA", "3140#", "912"), _c("Kansas City", "MO", "641##", "816"),
        _c("Albuquerque", "NM", "871##", "505"), _c("Burlington", "VT", "0540#", "802"),
        _c("Richmond", "VA", "232##", "804"), _c("Nashville", "TN", "372##", "615"),
        _c("Salt Lake City", "UT", "841##", "801"), _c("Ann Arbor", "MI", "4810#", "734"),
        _c("Grand Rapids", "MI", "495##", "616"), _c("Tucson", "AZ", "857##", "520"),
        _c("Des Moines", "IA", "503##", "515"), _c("Providence", "RI", "0290#", "401"),
        _c("Buffalo", "NY", "142##", "716"), _c("Rochester", "NY", "146##", "585"),
        _c("Boise", "ID", "837##", "208"), _c("Louisville", "KY", "402##", "502"),
        _c("Omaha", "NE", "681##", "402"), _c("Charleston", "SC", "2940#", "843"),
        _c("Portland", "ME", "041##", "207"), _c("Baltimore", "MD", "212##", "410"),
    ]}}

STREETS = {"US": [
    "Maple Street", "Oak Avenue", "Elm Street", "Main Street", "Park Avenue", "Washington Street", "Cedar Lane",
    "Lincoln Avenue", "Pine Street", "Lakeview Drive", "Hillcrest Road", "Jefferson Street", "Sycamore Lane",
    "Walnut Street", "Ridge Road", "Franklin Avenue", "Willow Creek Drive", "Chestnut Street", "Meadowbrook Lane",
    "Spring Street", "Prospect Avenue", "Union Street"]}

VENUES = {"US": [
    "Maplewood Community Center", "Cedar Lane Public Library", "Riverside Farmers Market Pavilion",
    "Lakeview Shopping Plaza", "Grace Fellowship Hall", "Hillcrest Senior Center", "Room 104, Harmon Hall",
    "Oak Avenue YM Recreation Center", "Union Street Grange Hall", "Westbrook Mall Atrium",
    "Jefferson Elementary Gymnasium", "Sycamore Commons Event Room", "Prospect Heights Neighborhood House"]}
