"""Round-4 regression checks across all 3000 prompts."""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_review_checks import quoted
rows = [json.loads(l) for l in open("final/poster_prompts_3000.jsonl", encoding="utf-8")]
C = collections.Counter(); EX = collections.defaultdict(list)


def hit(k, r):
    C[k] += 1
    if len(EX[k]) < 3:
        EX[k].append(r["id"])


AL = {"大豆": ["大豆", "豆粉", "黄豆", "酱油", "豆瓣", "豆豉", "磷脂", "豆浆", "腐竹", "豆腐", "味噌"], "花生": ["花生"], "鸡蛋": ["蛋"],
      "虾": ["虾"], "鱼": ["鱼"]}
for r in rows:
    p = r["prompt"]; t = "\n".join(quoted(p))
    ing = re.search(r"(?:配料|原料)[：】]([^」]+)", t)
    al = re.search(r"(?:过敏原信息|致敏物质提示|食物过敏原提示)：[^」]*", t)
    if r["variant"] == "clean" and ing and al:
        for w, keys in AL.items():
            if w in al.group(0) and not any(k in ing.group(1) for k in keys):
                hit("allergen_not_in_ingredients", r)
    if r["carrier"] in ("can", "bottle", "carton"):
        vis = re.search(r"包装外观：([^；]+)", p)
        if vis and r["carrier"] == "can" and "罐" not in vis.group(1):
            hit("can_carrier_non_can_visual", r)
        if vis and r["carrier"] == "bottle" and not any(w in vis.group(1) for w in ["瓶", "桶"]):
            hit("bottle_carrier_non_bottle_visual", r)
    if "「高钙」" in p and "「钙来源」" in p:
        hit("double_claim", r)
    if r["super_category"] == "保健品说明" and "GB 7101-2022" in t and any(k in t for k in ["饮料", "饮品", "口服液"]) and "standard_number_tamper" in r["tamper_types"]:
        hit("supp_std_tamper_not_anomalous", r)
    m = re.search(r"许可证编号：SC1(\d{2})", t)
    if m:
        c = int(m.group(1))
        if r["super_category"] == "保健品说明" and c == 27 and "保健食品" not in p.split("\n")[1] and "小蓝帽" not in p:
            hit("sc27_on_ordinary_food", r)
        if "肠" in r["product_or_title"] or "肉" in r["product_or_title"]:
            if c not in (4, 7, 11, 9, 31, 32) and "鱼" not in r["product_or_title"]:
                hit("meat_wrong_sc", r)
    mb = re.search(r"营养成分表（表头三列：「项目」｜「每(?:袋|份|粒|片|瓶)([\d.]+)(g|mL)」", p)
    ms = re.search(r"规格([\d.]+)(g|mL)/", p)
    if mb and ms and (mb.group(1), mb.group(2)) != (ms.group(1), ms.group(2)):
        hit("supp_spec_vs_basis", r)
    if "说明书" in p.split("\n")[0] and "喷码" in p:
        hit("inkjet_on_leaflet", r)
    if "万象汇" in p:
        hit("real_mall", r)
    if r["variant"] == "clean" and "manufacturer_info_tamper" in r["tamper_types"]:
        hit("x", r)
det = collections.Counter()
for r in rows:
    if r["variant"] != "clean" and "manufacturer_info_tamper" in r["tamper_types"]:
        d = " ".join(r["tamper_details"])
        city = re.findall(r"城市被改为「([^」]+)」", d)
        if city and city[0] not in r["prompt"].split("本图为")[0]:
            hit("mfr_tamper_missing", r)
print(json.dumps(C, ensure_ascii=False)); print(json.dumps(EX, ensure_ascii=False))
