"""Real-brand blacklist, part A: supermarkets, discounters, pharmacies, chains (lowercase, whole-word match).
Ambiguous everyday words are written as multi-word forms to avoid false hits on ordinary text."""
REAL_BRAND_BLACKLIST = [
    # UK
    "tesco", "sainsbury's", "sainsburys", "asda", "morrisons", "waitrose", "aldi", "lidl", "co-op food", "coop supermarket",
    "iceland foods", "marks & spencer", "m&s food", "ocado", "budgens", "londis", "nisa local", "spar", "eurospar",
    "booths supermarket", "farmfoods", "heron foods", "home bargains", "poundland", "costcutter", "holland & barrett",
    "boots pharmacy", "superdrug", "lloydspharmacy", "lloyds pharmacy", "well pharmacy",
    # Ireland
    "dunnes stores", "supervalu", "centra", "musgrave", "mace stores", "applegreen", "mccabes pharmacy", "hickey's pharmacy",
    # US
    "walmart", "kroger", "costco", "target stores", "whole foods", "whole foods market", "trader joe's", "safeway",
    "albertsons", "publix", "h-e-b", "meijer", "wegmans", "food lion", "giant eagle", "stop & shop", "hy-vee",
    "sprouts farmers market", "ralphs", "fred meyer", "harris teeter", "winn-dixie", "piggly wiggly", "shoprite",
    "acme markets", "jewel-osco", "sam's club", "bj's wholesale", "dollar general", "family dollar", "7-eleven",
    "amazon fresh", "the fresh market", "winco foods", "save a lot", "cvs", "cvs pharmacy", "walgreens", "rite aid",
    "duane reade", "gnc", "vitamin shoppe",
    # Canada
    "loblaws", "loblaw", "sobeys", "metro inc", "no frills", "real canadian superstore", "iga", "provigo", "freshco",
    "fortinos", "zehrs", "longo's", "farm boy", "t&t supermarket", "save-on-foods", "thrifty foods", "giant tiger",
    "food basics", "your independent grocer", "shoppers drug mart", "london drugs", "jean coutu", "pharmaprix",
    "rexall", "uniprix", "familiprix",
    # Europe
    "carrefour", "auchan", "e.leclerc", "leclerc", "intermarché", "intermarche", "super u", "système u", "monoprix",
    "franprix", "picard surgelés", "géant casino", "rewe", "edeka", "kaufland", "netto marken-discount", "penny markt",
    "globus hypermarkt", "tegut", "albert heijn", "jumbo supermarkten", "dirk van den broek", "hoogvliet", "delhaize",
    "colruyt", "mercadona", "dia supermercados", "eroski", "el corte inglés", "alcampo", "hipercor", "continente",
    "pingo doce", "esselunga", "conad", "coop italia", "eurospin", "despar", "migros", "denner", "billa", "hofer",
    "interspar", "ica supermarket", "willys", "hemköp", "rema 1000", "norgesgruppen", "kesko", "k-citymarket",
    "salling group", "føtex", "bilka", "biedronka", "żabka", "zabka", "stokrotka", "sklavenitis", "masoutis",
    "konzum", "mercator", "maxima", "rimi", "selver", "mega image", "dm-drogerie markt", "rossmann", "kruidvat",
    "etos", "apoteket", "apotek hjärtat", "matas",
    # Restaurant / coffee chains
    "mcdonald's", "burger king", "kfc", "subway restaurants", "starbucks", "costa coffee", "pret a manger", "greggs",
    "domino's", "pizza hut", "nando's", "tim hortons", "dunkin'", "krispy kreme", "chipotle mexican grill",
]
