"""Consistency helpers added after the 100-prompt manual review (keyword/ingredient agreement, container agreement, EAN prefixes)."""
import re

KW = {"奇亚籽": ["奇亚籽"], "燕麦": ["燕麦"], "菊粉": ["菊粉"], "牛磺酸": ["牛磺酸"], "草莓": ["草莓"], "蓝莓": ["蓝莓"], "核桃": ["核桃"],
      "杏仁": ["杏仁", "巴旦木"], "巴旦木": ["巴旦木", "杏仁"], "可可": ["可可"], "芝麻": ["芝麻"], "黄桃": ["黄桃"], "酸菜": ["酸菜"],
      "麻辣": ["花椒"], "香辣": ["辣椒"], "鳕鱼": ["鳕鱼"], "胶原": ["胶原"], "益生菌": ["菌"], "芒果": ["芒果"], "椰": ["椰"],
      "抹茶": ["抹茶"], "红枣": ["枣"], "枸杞": ["枸杞"], "紫薯": ["紫薯"], "南瓜": ["南瓜"], "香菇": ["香菇"], "牛肉": ["牛肉"],
      "鸡胸": ["鸡胸", "鸡肉"], "藜麦": ["藜麦"], "全麦": ["全麦"], "海盐": ["海盐"], "巧克力": ["巧克力", "可可"], "果香": ["果", "莓", "橙", "柠檬", "桃", "苹果", "葡萄"],
      "甜橙": ["橙"], "葡萄": ["葡萄"], "薄荷": ["薄荷"], "水蜜桃": ["桃"], "苹果": ["苹果"], "西柚": ["柚"], "百香果": ["百香果"], "荞麦": ["荞麦"],
      "坚果": ["仁", "坚果", "核桃", "杏仁", "腰果", "榛", "巴旦木", "夏威夷果"], "蜂蜜": ["蜂蜜"], "柠檬": ["柠檬"], "脐橙": ["橙"],
      "橙汁": ["橙"], "香橙": ["橙"], "玫瑰": ["玫瑰"], "桂花": ["桂花"], "黑糖": ["黑糖", "红糖"], "番茄": ["番茄"], "金枪鱼": ["金枪鱼"],
      "红豆": ["红豆", "赤小豆"], "绿豆": ["绿豆"], "维生素D": ["维生素D", "复合维生素", "维生素"], "维生素A": ["维生素A", "复合维生素", "维生素"],
      "B族维生素": ["维生素B", "复合维生素", "烟酰胺"], "锌": ["锌"], "DHA": ["DHA", "藻油", "鱼油"], "叶黄素": ["叶黄素"],
      "乳清": ["乳清"], "果粒": ["果", "莓", "桃", "芒"], "鸡蛋": ["鸡蛋", "蛋"], "猪肉": ["猪肉"], "玉米": ["玉米"], "乳酸菌": ["菌"], "橄榄油": ["橄榄油"], "稻米油": ["稻米油"]}


PLACE_TOKENS = ["西湖", "赣南", "砀山", "新疆", "云南", "内蒙古", "宁夏", "东北", "五常", "重庆", "四川", "广式", "潮汕", "台湾", "香港",
                "日式", "韩式", "泰式", "法式", "意式", "新西兰", "澳洲", "阿克苏", "库尔勒", "烟台", "赣州", "眉山"]
ANIMAL = ["牛油", "猪", "牛肉", "鸡", "鱼", "虾", "蟹", "骨汤", "肉"]
NUT_WORDS = {"维生素D": "vitd", "锌": "zinc", "钙": "calcium", "铁": "iron", "膳食纤维": "fiber", "维生素C": "vitc"}


def name_conflict(name, ings):
    j = "".join(ings)
    return "素" in name and any(a in j for a in ANIMAL)


def has_place(text):
    return any(p in text for p in PLACE_TOKENS)


def nutrient_mention_ok(text, nut_keys):
    """selling line naming an added nutrient must have that row in the table; numeric nutrient amounts are never allowed
    (they cannot be kept consistent with every pack size)."""
    if re.search(r"\d+(\.\d+)?\s*(g|克|mg|毫克)\s*(优质)?(蛋白|膳食纤维|纤维|钙)", text) or re.search(r"(蛋白质?|纤维|钙)[^，。]{0,4}\d+(\.\d+)?\s*(g|克|mg)", text):
        return False
    for w, k in NUT_WORDS.items():
        if w in text.replace("钙片", "") and k not in nut_keys:
            return False
    return True


def kw_missing(text, ings):
    j = "".join(ings)
    t = text.replace("拿铁", "").replace("铁盒", "").replace("乳酸菌味", "")
    return [k for k, alts in KW.items() if k in t and not any(a in j for a in alts)]


CONTAINER = [("can", ["易拉罐", "铝罐", "马口铁罐", "铁罐", "罐装", "罐"]), ("carton", ["利乐", "屋顶盒", "纸盒", "砖"]),
             ("bottle", ["瓶"]), ("barrel", ["桶"]), ("cup", ["杯"]), ("bag", ["袋", "包装膜", "条装"]), ("box", ["盒", "礼盒", "箱"])]


def container_class(text):
    for k, ws in CONTAINER:
        if any(w in text for w in ws):
            return k
    return None


GS1 = {"新西兰": "94", "澳大利亚": "93", "马来西亚": "955", "泰国": "885", "意大利": "80", "西班牙": "84", "比利时": "54",
       "韩国": "880", "日本": "45", "德国": "40", "丹麦": "57", "越南": "893"}
FOREIGN_MFR = {"新西兰": "Greenvale Foods Ltd.", "澳大利亚": "Southern Cross Dairy Pty Ltd.", "马来西亚": "Golden Palm Food Industries Sdn. Bhd.",
               "泰国": "Siam Harvest Co., Ltd.", "意大利": "Casa Verdi S.r.l.", "西班牙": "Huerta del Sol S.L.", "比利时": "Maison Leroux S.A.",
               "韩国": "Hanbit Foods Co., Ltd.", "日本": "Sakura Hill Foods Co., Ltd.", "德国": "Nordfeld Foods GmbH",
               "丹麦": "Lindholm Mejeri A/S", "越南": "Mekong Fresh Foods JSC"}


def ean13(rng, prefix="69"):
    d = [int(c) for c in prefix] + [rng.randint(0, 9) for _ in range(12 - len(prefix))]
    t = sum(x * (3 if i % 2 else 1) for i, x in enumerate(d))
    d.append((10 - t % 10) % 10)
    s = "".join(map(str, d))
    return f"{s[0]} {s[1:7]} {s[7:]}"


def serving_pack_ok(net, size):
    m = re.search(r"([\d.]+)\s*g\s*[×x]", net)
    return (m is None) or abs(float(m.group(1)) - size) < 0.01
