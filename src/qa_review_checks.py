"""QA extension: automated checks for the defect classes found in the 100-prompt manual review (round 1)."""
import re
import brands as _B
from consistency import kw_missing as _kwm

_CITY_OF_CODE = {}
for _c, _code in _B.AREA.items():
    _CITY_OF_CODE.setdefault(_code, set()).add(_c)
_ALL_CITIES = [c[1] for c in _B.CITIES]
RULE_MARK = "本提示词中「」内的内容为必须逐字呈现的文字"


def quoted(p):
    return re.findall("「(.*?)」", p.split(RULE_MARK)[0], flags=re.S)


def review_checks(r):
    p = r["prompt"]
    q = quoted(p)
    txt = "\n".join(q)
    bad = []
    if "右上角左上角" in p or "左上角左上角" in p or "。。" in p or re.search(r"。；|；。", txt):
        bad.append("template_glitch")
    if re.search(r"适宜人群：适宜人群", txt):
        bad.append("dup_prefix")
    for m in re.finditer(r"许可证编号：SC(\d+)", txt):
        if len(m.group(1)) != 14:
            bad.append("sc_len")
    if re.search(r"参与费用(凭|免费|按)", p):
        bad.append("fee_wording")
    if "爆炸贴" in p and r["super_category"] == "食品标签":
        bad.append("price_sticker_on_label")
    body = p.split("本图为")[0]
    if "带删除线" in body and not re.search(r"原价¥", txt):
        bad.append("strike_without_price")
    n_tables = p.count("营养成分表（表头") + p.count("【营养成分表】") + txt.count("营养成分表（每")
    if n_tables > 1:
        bad.append("two_nutrition_tables")
    ing = re.search(r"(?:配料|原料)[：】]([^」]+)", txt)
    if ing and r["super_category"] in ("食品标签", "商业广告"):
        nm = r["product_or_title"]
        b = r.get("brand_or_organizer") or ""
        nm = nm.replace(b, "").replace("牌", "", 1) if b else nm
        if _kwm(nm, [ing.group(1)]):
            bad.append("name_kw_not_in_ingredients")
    if r["super_category"] in ("公益海报", "活动宣传"):
        cities = {c for c in _ALL_CITIES if c in txt}
        for m in re.finditer(r"(0\d{2,3})-\d{7,8}", txt):
            cs = _CITY_OF_CODE.get(m.group(1))
            if cs and cities and not (cs & cities):
                bad.append("area_code_city_mismatch")
        if len(cities) > 1:
            bad.append("multi_city")
    if re.search(r"咨询电话[：:]12315", txt):
        bad.append("12315_as_consult")
    return sorted(set(bad))
