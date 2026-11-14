# United Kingdom (England, Scotland, Wales, Northern Ireland). Phones: Ofcom drama ranges.
def _c(city, area, pc, ph):
    return {"city": city, "area": area, "postcode": pc, "phone": ph}


COUNTRIES = {"UK": {
    "name": "United Kingdom", "region": "UK", "currency": "GBP", "lang_context": "native", "date_style": "eu",
    "phone_fmt": ["0161 496 0###", "020 7946 0###", "0113 496 0###", "0117 496 0###", "0121 496 0###",
                  "0131 496 0###", "0141 496 0###", "029 2018 0###", "028 9018 0###", "01632 960###",
                  "07700 900###"],
    "postcode_fmt": ["LS# #XX", "M## #XX", "BS# #XX", "EH# #XX", "G## #XX", "CF## #XX", "BT# #XX", "NR# #XX"],
    "cities": [
        _c("London", "Greater London", "SE1# #XX", "020 7946 0###"),
        _c("Manchester", "Greater Manchester", "M1# #XX", "0161 496 0###"),
        _c("Leeds", "West Yorkshire", "LS1# #XX", "0113 496 0###"),
        _c("Sheffield", "South Yorkshire", "S1 #XX", "0114 496 0###"),
        _c("Bristol", "City of Bristol", "BS1 #XX", "0117 496 0###"),
        _c("Birmingham", "West Midlands", "B1# #XX", "0121 496 0###"),
        _c("Nottingham", "Nottinghamshire", "NG7 #XX", "0115 496 0###"),
        _c("Leicester", "Leicestershire", "LE1 #XX", "0116 496 0###"),
        _c("Liverpool", "Merseyside", "L1# #XX", "0151 496 0###"),
        _c("Newcastle upon Tyne", "Tyne and Wear", "NE1 #XX", "0191 498 0###"),
        _c("Reading", "Berkshire", "RG1 #XX", "0118 496 0###"),
        _c("Norwich", "Norfolk", "NR2 #XX", "01603 496###"),
        _c("York", "North Yorkshire", "YO1 #XX", "01904 496###"),
        _c("Brighton", "East Sussex", "BN1 #XX", "01273 496###"),
        _c("Cambridge", "Cambridgeshire", "CB2 #XX", "01223 496###"),
        _c("Edinburgh", "City of Edinburgh", "EH1 #XX", "0131 496 0###"),
        _c("Glasgow", "Glasgow City", "G2 #XX", "0141 496 0###"),
        _c("Aberdeen", "Aberdeen City", "AB10 #XX", "01224 496###"),
        _c("Dundee", "Dundee City", "DD1 #XX", "01382 496###"),
        _c("Inverness", "Highland", "IV2 #XX", "01463 496###"),
        _c("Cardiff", "South Glamorgan", "CF10 #XX", "029 2018 0###"),
        _c("Swansea", "West Glamorgan", "SA1 #XX", "01792 496###"),
        _c("Newport", "Gwent", "NP20 #XX", "01633 496###"),
        _c("Wrexham", "Clwyd", "LL11 #XX", "01978 496###"),
        _c("Belfast", "County Antrim", "BT1 #XX", "028 9018 0###"),
        _c("Derry", "County Londonderry", "BT48 #XX", "028 7149 6###"),
        _c("Lisburn", "County Antrim", "BT28 #XX", "028 9249 6###"),
        _c("Newry", "County Down", "BT35 #XX", "028 3049 6###"),
    ]}}

STREETS = {"UK": [
    "Mill Lane", "Church Lane", "Station Road", "Victoria Street", "Orchard Close", "Meadow Way", "Park Avenue",
    "Chapel Street", "The Crescent", "Willow Grove", "Kings Road", "Queensway Parade", "Elm Terrace",
    "Brook Street", "Market Place", "Hawthorn Drive", "Albert Road", "Riverside Walk", "Beech Avenue",
    "St Andrew's Road", "Glebe Close", "Thornbury Lane"]}

VENUES = {"UK": [
    "Millbrook Community Centre", "St Aidan's Church Hall", "Hawthorn Lane Library", "Riverside Market Hall",
    "The Kingsgate Shopping Centre", "Elmfield Village Hall", "Lecture Theatre 2, Westfield Building",
    "Orchard Street Leisure Centre", "Brookside Methodist Hall", "The Corn Exchange Rooms",
    "Willowdene Family Hub", "Ashgrove Students' Union Atrium"]}
