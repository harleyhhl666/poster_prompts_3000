"""Validate library files. Usage: python src/validate_libs.py [module ...]"""
import importlib
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
ALLERGENS = {"麸质", "甲壳", "鱼", "蛋", "花生", "大豆", "乳", "坚果"}
VERIFIED_STD = {"GB 19645-2010", "GB 25190-2010", "GB 25191-2010", "GB 19302-2025", "GB 19644-2024", "GB 7101-2022",
                "GB 7099-2015", "GB 7100-2015", "GB 2759-2015", "GB 19295-2021", "GB 7098-2015", "GB 14963-2011",
                "GB 2749-2015", "GB 2730-2015", "GB 5420-2021", "GB 25192-2022"}
REAL_BRANDS = ["可口可乐", "伊利", "蒙牛", "元气森林", "雀巢", "汤臣倍健", "安利", "麦当劳", "肯德基", "山姆", "沃尔玛", "农夫山泉",
               "光明", "君乐宝", "娃哈哈", "康师傅", "统一", "旺旺", "良品铺子", "三只松鼠", "百草味", "海天", "李锦记", "达利园",
               "奥利奥", "乐事", "德芙", "士力架", "星巴克", "瑞幸", "喜茶", "奈雪", "盒马", "永辉", "家乐福", "华润万家", "善存",
               "钙尔奇", "Swisse", "健合", "养生堂", "脑白金", "东阿阿胶", "同仁堂", "修正", "999", "惠氏", "美赞臣", "飞鹤", "贝因美",
               "卫龙", "思念", "三全", "湾仔码头", "金龙鱼", "鲁花", "福临门", "太太乐", "老干妈", "双汇", "雨润", "金锣", "王老吉",
               "加多宝", "红牛", "东鹏", "脉动", "怡宝", "百岁山", "维他", "豆本豆", "六个核桃", "椰树", "北冰洋", "冰峰", "汇源",
               "美年达", "雪碧", "芬达", "百事", "桃李", "曼可顿", "好丽友", "徐福记", "盼盼", "嘉华", "稻香村", "五芳斋", "安佳", "佳沃"]
errs = []


def e(msg):
    errs.append(msg)


def scan_brands(obj, where):
    s = repr(obj)
    for b in REAL_BRANDS:
        if b in s:
            e(f"{where}: contains real brand '{b}'")


def check_food(mod):
    arcs = mod.ARCHETYPES
    ids = set()
    for a in arcs:
        w = f"{mod.__name__}:{a.get('id')}"
        for k in ["id", "sub_category", "product_type", "names", "form", "packages", "recipes", "nut_keys", "basis",
                  "claims_ok", "selling", "exag_subtle", "exag_strong", "shelf", "shelf_tamper", "storage", "usage",
                  "standard", "visual"]:
            if k not in a:
                e(f"{w}: missing {k}")
        if a.get("id") in ids:
            e(f"{w}: dup id")
        ids.add(a.get("id"))
        for core in ["energy", "protein", "fat", "carb", "sodium"]:
            if core not in a.get("nut_keys", []):
                e(f"{w}: nut_keys missing {core}")
        if a.get("basis") == "serving" and not a.get("serving"):
            e(f"{w}: serving basis but no serving")
        for r_i, r in enumerate(a.get("recipes", [])):
            tot = sum(x["p"] for x in r["ing"])
            if not 95 <= tot <= 105:
                e(f"{w} recipe{r_i}: ingredient % sum {tot:.1f}")
            for x in r["ing"]:
                for al in x.get("a", []):
                    if al not in ALLERGENS:
                        e(f"{w}: bad allergen {al}")
            nut = r["nut"]
            for k in a.get("nut_keys", []):
                if k != "energy" and k not in nut:
                    e(f"{w} recipe{r_i}: nut missing {k}")
            if a["form"] == "solid":
                s = nut.get("protein", 0) + nut.get("fat", 0) + nut.get("carb", 0) + nut.get("fiber", 0)
                if s > 100:
                    e(f"{w} recipe{r_i}: macro sum {s}>100")
            if not any(x.get("hero") for x in r["ing"]) and len(r["ing"]) >= 4:
                e(f"{w} recipe{r_i}: no hero ingredient (ok only for single-ingredient foods)")
        st = a.get("standard")
        if st and st.get("code") not in VERIFIED_STD:
            e(f"{w}: unverified standard {st}")
        ws = a.get("wrong_standard")
        if ws and ws not in VERIFIED_STD:
            e(f"{w}: unverified wrong_standard {ws}")
        if ("无糖" in a.get("claims_ok", []) or "低糖" in a.get("claims_ok", [])) and "sugar" not in a.get("nut_keys", []):
            e(f"{w}: sugar claim without sugar row")
        scan_brands(a, w)
    print(f"{mod.__name__}: {len(arcs)} archetypes")


def check_list(mod, attr, required):
    items = getattr(mod, attr)
    ids = set()
    for a in items:
        w = f"{mod.__name__}:{a.get('id')}"
        for k in required:
            if k not in a:
                e(f"{w}: missing {k}")
        if a.get("id") in ids:
            e(f"{w}: dup id")
        ids.add(a.get("id"))
        scan_brands(a, w)
    print(f"{mod.__name__}: {len(items)} entries")
    return items


def main(mods):
    for m in mods:
        try:
            mod = importlib.import_module(m)
        except Exception as ex:
            e(f"{m}: import error {ex!r}")
            continue
        if hasattr(mod, "ARCHETYPES"):
            check_food(mod)
        if hasattr(mod, "SUPPLEMENTS"):
            items = check_list(mod, "SUPPLEMENTS", ["id", "sub_category", "reg_type", "names", "dosage_form", "spec", "price",
                                                    "raw_materials", "hero_first_tamper", "allergens", "components",
                                                    "health_function", "suitable", "unsuitable", "usage", "cautions", "shelf",
                                                    "shelf_tamper", "storage", "normal_copy", "exag_subtle", "exag_strong",
                                                    "population_tamper", "visual"])
            for s in items:
                a = sorted(x.strip() for x in s["raw_materials"].replace("，", "、").split("、"))
                b = sorted(x.strip() for x in s["hero_first_tamper"].replace("，", "、").split("、"))
                if a != b:
                    e(f"supp {s['id']}: hero_first_tamper items differ from raw_materials")
                if a == b and s["raw_materials"] == s["hero_first_tamper"]:
                    e(f"supp {s['id']}: hero_first_tamper identical")
                for al in s["allergens"]:
                    if al not in ALLERGENS:
                        e(f"supp {s['id']}: bad allergen {al}")
        if hasattr(mod, "WELFARE"):
            items = check_list(mod, "WELFARE", ["id", "sub_category", "titles", "subtitles", "organizer_types", "sections",
                                                "numbers", "key_warning", "misinfo_subtle", "misinfo_strong", "cta",
                                                "has_event", "visual_styles", "visual_motif"])
            for w in items:
                alltext = " ".join(w["subtitles"]) + " ".join(" ".join(s["items"]) for s in w["sections"])
                for n in w["numbers"]:
                    if n["text"] not in alltext:
                        e(f"welfare {w['id']}: number text not found verbatim: {n['text']}")
                if w["key_warning"] in alltext:
                    pass
        if hasattr(mod, "EVENTS"):
            check_list(mod, "EVENTS", ["id", "sub_category", "commercial", "title_patterns", "agenda", "perks", "rules",
                                       "hidden_condition", "quota", "fee", "venue_types", "duration_days", "daily_hours",
                                       "health_related", "visual_styles", "visual_motif"])
    if errs:
        print(f"{len(errs)} ERRORS")
        for x in errs:
            print(" -", x)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main(sys.argv[1:] or ["lib_food_a", "lib_food_b", "lib_food_c", "lib_supplement", "lib_welfare", "lib_event"])
