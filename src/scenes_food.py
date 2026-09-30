"""Scenes: 食品标签 (food_label) and 商业广告 (commercial ad) prompt builders."""
import copy
from common import rng_for, fmt_date, shelf_str, money, money_short, md_cn, add_days
from food import (make_food_spec, ingredients_line, nutrition_table_text, dates_lines, batch_line, standard_lines,
                  producer_lines, FOOD_OPS, allergen_text)
from promo import FESTIVALS, make_promo, promo_date_text, price_block, rules_lines, PROMO_OPS
from visual import PALETTES, PHOTO_ARTIFACTS, REALISM, TEXT_RULE_BASE, TEXT_RULE_TABLE, TEXT_RULE_QUOTE, FONT_NOTE


def Q(s):
    return f"「{s}」"


def QL(lines, sep="；"):
    return sep.join(Q(x) for x in lines if x)


# ------------------------------------------------------------------ shared blocks
def nut_block(spec, style="table"):
    head = f"营养成分表（表头三列：{Q('项目')}｜{Q(spec['basis_label'])}｜{Q('营养素参考值%')}），逐行为："
    rows = nutrition_table_text(spec)
    body = "；".join(Q(r) for r in rows)
    extra = []
    if spec["basis"] == "serving":
        extra.append(f"表格下方小字{Q('本品每袋约含' + str(spec['serving']['size']) + spec['serving']['unit'].replace('g','克').replace('mL','毫升') + '，以上为每份数值')}" if False else "")
    return head + body + "。"


def allergen_block(spec):
    out = []
    if spec["allergen_statement"]:
        out.append(spec["allergen_statement"])
    if spec["may_contain"]:
        out.append(spec["may_contain"])
    return out


def pop_line(pop):
    pop = pop.strip()
    for pre in ("适宜人群：", "适宜人群:", "适用人群：", "不适宜人群："):
        if pop.startswith(pre):
            return pop
    return "适宜人群：" + pop


def info_core_lines(spec, include_name=True, include_type=True):
    L = []
    if include_name:
        L.append(f"产品名称：{spec['name']}")
    if include_type:
        L.append(f"产品类型：{spec['product_type']}")
    return L


def date_batch_lines(spec, with_expiry=True):
    L = dates_lines(spec)
    if not with_expiry:
        L = L[:2]
    L.append(batch_line(spec))
    return L


def inkjet_text(spec):
    t = spec["prod_date_true"]
    b = spec.get("batch2") or spec["batch_true"]
    s = f"{t.strftime('%Y/%m/%d')} {b}"
    if spec.get("expiry_ink"):
        s += f" 保质期至{spec['expiry_ink'].strftime('%Y/%m/%d')}"
    return s


def front_claim_lines(spec):
    L = []
    if spec.get("attr_text"):
        L.append(spec["attr_text"])
    L += spec["claims"][:3]
    if spec.get("allergen_free_claim"):
        L.append(spec["allergen_free_claim"])
    return L


def selling_lines(spec):
    L = list(spec["headline_extra"][1:] if spec["headline_extra"] else []) + list(spec["selling"])
    h0 = spec["headline_extra"][0] if spec["headline_extra"] else None
    return [x for x in dict.fromkeys(L) if x != h0]


def net_front(spec):
    if spec.get("count_shown2"):
        return f"{spec['pack']['net']}×{spec['count_shown2']}{spec['unit_word']}"
    if spec.get("net_shown2"):
        return spec["net_shown2"] if spec["count"] == 1 else f"{spec['net_shown2']}×{spec['count']}{spec['unit_word']}"
    return spec["net_text"]


FIELD_CN = {"production_date": "生产日期", "shelf_life": "保质期", "expiry_date": "保质期至", "batch": "批号", "batch_number": "批号",
            "ingredients": "配料表", "raw_materials": "原料表", "allergen_statement": "过敏原信息", "front_claim": "正面宣传语",
            "selling_claim": "卖点文案", "headline_claim": "宣传语", "promo_copy": "宣传语", "nutrition": "营养成分表",
            "nutrition_table": "营养成分表", "nutrient_claim": "营养声称", "net_content": "净含量", "count": "规格件数",
            "standard_number": "标准号", "manufacturer_address": "生产地址", "manufacturer": "生产者信息", "origin": "产地",
            "storage": "贮存条件", "product_attribute": "产品属性宣称", "population": "适宜人群", "suitable_population": "适宜人群",
            "unsuitable_population": "不适宜人群", "usage_warning": "食用方法", "storage_after_opening": "贮存条件",
            "promo_price": "价格", "discount_math": "折扣与价格", "second_item_price": "价格", "member_price": "会员价",
            "combo_price": "组合价", "threshold": "满减规则", "bundle_rule": "活动规则", "headline_vs_rules": "价格与活动规则",
            "original_price": "原价", "promo_end_date": "活动日期", "promo_weekday": "活动日期", "promo_start_date": "活动日期",
            "promo_period": "活动期限", "promo_rule": "活动规则", "gift_condition": "赠品规则", "quota": "名额",
            "health_function": "保健功能", "warning_zone": "警示用语", "cautions": "注意事项", "approval_number": "批准文号",
            "function": "保健功能", "evidence_claim": "宣传语", "key_fact": "科普要点", "section_item": "科普要点",
            "key_warning": "重点提示", "event_weekday": "活动日期", "event_date": "活动日期", "venue": "活动地点",
            "hotline": "联系电话", "source_note": "资料来源", "event_end_date": "活动日期", "event_period": "活动期限",
            "venue_address": "活动地址", "fee": "费用说明", "rules": "活动须知", "disclaimer": "免责提示", "agenda": "活动流程表"}


def fields_cn(tampers):
    out = []
    for t in tampers:
        for f in t["field"].split("+"):
            f = f.split(".")[0]
            c = FIELD_CN.get(f, "相关字段")
            if c not in out:
                out.append(c)
    return "、".join(out)


def anomaly_note(tampers, kind="商业设计"):
    if not tampers:
        return "本图为正常对照版本：所有字段严格按给定内容呈现即可。"
    return ("本图为研究用样本：给定文字中的部分内容（涉及" + fields_cn(tampers) + "）按研究设计包含不实、夸大、缺失或与其他位置不一致的信息。"
            "请严格按给定文字逐字呈现，不要自动纠正、补全或统一；不要用颜色、圈注、箭头、放大、删除线或任何警示标记突出这些内容，"
            f"它们必须与周围文字保持相同的字体、字号和排版风格，使整张图看起来是一张完全正常的{kind}。")


def text_rules(has_table=True):
    s = TEXT_RULE_QUOTE + TEXT_RULE_BASE
    if has_table:
        s += TEXT_RULE_TABLE
    return s + FONT_NOTE + "。"


# ------------------------------------------------------------------ label scenes
LABEL_CARRIERS = [
    # key, weight, aspect, realism, description template
    ("back_flat", 3, ["3:4", "4:5", "1:1"], "studio", "袋装/盒装食品包装背面平铺于浅色桌面的俯拍特写，包装占画面约90%"),
    ("bottle", 2, ["3:4", "4:5"], "studio", "饮料/调味品瓶身环绕式标签的正面特写，标签信息面正对镜头"),
    ("can", 1, ["1:1", "4:5"], "studio", "圆柱形罐装食品的罐身标签特写，信息面正对镜头"),
    ("pair", 3, ["16:9", "4:3"], "studio", "同一包装的正面与背面左右并列平铺展示（左为正面，右为背面），俯拍"),
    ("carton", 2, ["3:4", "1:1"], "studio", "纸盒包装（利乐砖/纸盒）侧面信息面的特写，轻微45度角展示可见盒子立体感"),
    ("outer_box", 1, ["4:3", "16:9"], "scene", "仓库/门店后仓中瓦楞纸外箱侧面贴着的白底外箱标签特写"),
    ("import", 1, ["3:4", "4:5"], "studio", "进口食品原包装背面（外文印刷背景）上加贴的白底中文背标贴纸特写"),
    ("frozen", 1, ["3:4", "4:5"], "scene", "冷冻食品包装袋背面在超市冷柜边被拍摄的特写"),
    ("giftbox", 1, ["4:3", "16:9"], "studio", "食品礼盒底部/背面信息标签特写，礼盒侧边可见烫金图案"),
    ("handheld", 2, ["3:4", "9:16"], "phone", "在超市货架前用手拿起商品翻到背面拍摄的手机实拍照"),
]
LABEL_LAYOUTS = {
    "A": "信息区分为左右两栏：左栏从上到下依次为产品名称、产品类型、配料表、过敏原信息；右栏为营养成分表（方框表格），表格下方为贮存条件与食用方法；最底部通栏为日期、批号、标准号、生产商等信息，最右下角为条形码",
    "B": "信息区从上到下通栏排列：顶部为产品名称与产品类型，其下为完整配料表与过敏原提示，中部左侧为营养成分表、中部右侧为净含量/贮存/食用方法，底部为生产日期、保质期、批号、标准号、生产商信息与条形码",
    "C": "信息区为三栏：左栏为配料表与过敏原提示，中栏为营养成分表，右栏为净含量、日期、批号、标准号、贮存条件；底部通栏为生产商、地址、许可证编号、服务热线和条形码",
    "D": "信息区上方为一行彩色品名条，下方左侧大面积为营养成分表，右侧为配料表与过敏原提示，底部一排小字为日期、批号、标准号和生产者信息",
}


def layout_text(spec, key):
    t = LABEL_LAYOUTS[key]
    if not (spec["allergen_statement"] or spec.get("may_contain")):
        for a in ["、过敏原信息", "与过敏原提示", "、过敏原提示", "与过敏原信息"]:
            t = t.replace(a, "")
    return t


def label_info_text(spec, layout_key):
    """Returns ordered list of (block_title, content) for a back label."""
    blocks = []
    blocks.append(("产品名称与类型", QL(info_core_lines(spec))))
    blocks.append(("配料表", Q(ingredients_line(spec))))
    al = allergen_block(spec)
    if al:
        blocks.append(("过敏原信息（紧邻配料表，与配料表同样字号）" if spec["allergen_statement"] else "共线生产提示（紧邻配料表）", QL(al)))
    if spec.get("hero_pct_line"):
        blocks.append(("配料定量标示（配料表末尾）", Q(spec["hero_pct_line"])))
    for x in spec.get("extra_label_lines") or []:
        blocks.append(("配料补充说明（配料表下方）", Q(x)))
    blocks.append(("营养成分表", nut_block(spec)))
    if spec.get("function_claim"):
        blocks.append(("营养成分表下方的营养声称说明", Q(spec["function_claim"])))
    netl = [f"净含量：{spec['net_text']}" if spec["count"] == 1 else f"净含量/规格：{spec['net_text']}"]
    if spec.get("outer_case"):
        n_case = spec["count"] if spec["count"] > 1 else 12
        netl = [f"规格：{spec['net_text'] if spec['count'] > 1 else spec['net_text'] + '×' + str(n_case) + spec['unit_word']}/箱"]
    blocks.append(("净含量", QL(netl)))
    blocks.append(("日期与批号", QL(date_batch_lines(spec))))
    sl = standard_lines(spec)
    if sl:
        blocks.append(("标准号", QL(sl)))
    blocks.append(("贮存条件", Q("贮存条件：" + spec["storage"])))
    if spec.get("usage"):
        blocks.append(("食用方法", Q("食用方法：" + spec["usage"])))
    if spec.get("population"):
        blocks.append(("适宜人群", Q(pop_line(spec["population"]))))
    blocks.append(("生产者信息", QL(producer_lines(spec))))
    blocks.append(("条形码", f"条形码图形，下方数字{Q(spec['ean'])}"))
    if spec["digital_label"]:
        blocks.append(("数字标签", f"一个小二维码，旁边小字{Q('扫码查看数字标签')}"))
    return blocks


def render_label(spec, g, tampers):
    rng = rng_for("labelrender", g["gid"])
    car = g["carrier"]
    ckey, _, _, realism, cdesc = car
    pal = PALETTES[g["palette"]]
    parts = []
    parts.append(f"生成一张{g['aspect']}比例的中国预包装食品标签图像：{cdesc}。{REALISM[realism]}。")
    parts.append(f"产品为虚构品牌{Q(spec['brand'])}的{Q(spec['name'])}（{spec['product_type']}），包装外观：{spec['visual']}；"
                 f"标签沿用包装主色，信息区为白底深色文字，分隔线与小标题使用包装主色。")
    if ckey == "pair":
        front = [f"品牌标志与品牌名{Q(spec['brand'])}位于正面顶部", f"正面中部大字品名{Q(spec['name_core'])}"]
        fcl = front_claim_lines(spec)
        if fcl:
            front.append("品名下方的圆角标签依次为" + QL(fcl, "、"))
        sl = selling_lines(spec)
        if spec["headline_extra"]:
            front.append(f"正面醒目的宣传语横幅{Q(spec['headline_extra'][0])}")
        if sl:
            front.append("正面中下部卖点短句" + QL(sl[:3], "、"))
        front.append(f"正面右下角净含量{Q('净含量：' + net_front(spec))}")
        parts.append("【左侧：包装正面】" + "；".join(front) + "；正面中央配有产品实物/食材摄影图。")
        parts.append("【右侧：包装背面】背面为白底信息区，" + layout_text(spec, g["layout"]) + "。背面文字内容如下：")
    else:
        parts.append("【版式】标签顶部为品牌名" + Q(spec["brand"]) + "的小标志；" + layout_text(spec, g["layout"]) + "。")
        fcl = front_claim_lines(spec)
        sl = selling_lines(spec)
        extra = []
        if spec["headline_extra"]:
            extra.append(Q(spec["headline_extra"][0]))
        if fcl:
            extra += [Q(x) for x in fcl]
        if sl:
            extra += [Q(x) for x in sl[:2]]
        extra = list(dict.fromkeys(extra))
        if extra:
            parts.append("标签顶部品名旁的“产品特点”小色块内写：" + "、".join(extra) + "。")
        if spec.get("net_shown2") or spec.get("count_shown2"):
            parts.append(f"标签顶部右侧大号数字标示{Q('净含量 ' + net_front(spec))}。")
        parts.append("标签信息文字内容如下：")
    for i, (t, c) in enumerate(label_info_text(spec, g["layout"]), 1):
        parts.append(f"{i}. {t}：{c}")
    if spec.get("inkjet_on") or spec.get("expiry_ink"):
        parts.append(f"另在标签{rng.choice(['右上角', '顶部封口', '底部空白处'])}有一处黑色点阵喷码（喷码字体，清晰可读）：{Q(inkjet_text(spec))}。")
    if spec["imported"]:
        ii = spec["import_info"]
        parts.append(f"中文贴纸四周可见被部分遮住的原包装外文印刷，外文部分只作为背景纹理，不需要可读；中文贴纸内容必须完整清晰。")
    arts = g["artifacts"]
    if arts:
        parts.append("真实感细节：" + "；".join(PHOTO_ARTIFACTS[a] for a in arts) + "。所有标签文字区域依然必须清晰锐利、可逐字辨认。")
    parts.append(anomaly_note(tampers, "预包装食品标签"))
    parts.append(text_rules(True))
    return "\n".join(parts)


# ------------------------------------------------------------------ commercial ad scenes
AD_SCENES = [
    # key, sub_category, aspect options, realism, description
    ("super_poster", "超市促销海报", ["3:4", "4:5"], "flat", "一张中国连锁超市的单品促销海报（平面设计稿）"),
    ("ecom_detail", "电商详情页", ["9:16"], "flat", "一张电商商品详情页长图（手机端竖版，自上而下分为多个模块）"),
    ("festival", "节日促销海报", ["4:5", "3:4"], "flat", "一张节日主题的食品促销海报"),
    ("standee", "门店立牌/展架", ["9:16"], "scene", "超市/便利店入口处X展架（易拉宝）促销海报的实拍照，展架占画面主体"),
    ("table_card", "桌卡/台卡", ["1:1", "4:5"], "phone", "放在收银台或试吃台上的亚克力三角台卡实拍照，台卡正面海报占画面主体"),
    ("shelf", "货架宣传牌", ["16:9", "4:3"], "scene", "超市货架陈列区实拍：货架上摆放该商品，货架前沿插有促销爆炸贴与白底价签"),
    ("launch", "新品上市海报", ["4:5", "3:4"], "studio", "一张极简品牌风的新品上市海报，含摄影棚产品摄影"),
    ("giftbox_ad", "礼盒广告", ["16:9", "4:3"], "studio", "一张横版礼盒促销广告图，礼盒打开展示内部小包装"),
    ("flash_mobile", "秒杀活动页", ["9:16"], "flat", "一张手机APP秒杀活动页面截图风格的促销图"),
    ("glass_door", "门店玻璃门海报", ["3:4", "4:5"], "phone", "贴在社区生鲜超市玻璃门内侧的促销海报，被路人用手机正面拍下"),
    ("popup", "快闪店宣传海报", ["4:5", "9:16"], "flat", "一张年轻潮流风的品牌快闪店宣传海报"),
    ("leaflet", "超市宣传单页", ["3:4"], "flat", "一张超市每周特价宣传单页（DM单）中的整版单品专题"),
]
AD_STYLE = {
    "super_poster": "超市促销风：大号爆炸贴价格、高对比色块、商品实物图居中",
    "ecom_detail": "电商详情页风：模块化分区、圆角信息卡片、图标化卖点",
    "festival": "中国节日风：节日元素（灯笼/祥云/月亮/烟花）点缀，喜庆但信息区清爽",
    "standee": "商场促销风：竖长画面，上部品牌与主视觉，下部价格与规则",
    "table_card": "简洁台卡风：信息紧凑，价格醒目",
    "shelf": "超市货架环境：真实陈列，价签与爆炸贴为信息主体",
    "launch": "极简品牌风/高端食品风：大面积留白、精致字体、柔光产品摄影",
    "giftbox_ad": "高端礼盒风：烫金/描金细节，礼盒内容清单排版整齐",
    "flash_mobile": "电商秒杀风：倒计时条、抢购按钮、价格标签",
    "glass_door": "社区门店风：海报贴在玻璃门上，可见门把手与店内环境",
    "popup": "年轻潮流风：撞色几何图形、贴纸元素、手写感标题",
    "leaflet": "超市DM单风：密集的信息排版、价格色块、虚线分隔",
}


def ad_info_box(spec, full=True):
    L = []
    L.append(Q(f"品名：{spec['name']}"))
    L.append(Q(f"规格：{spec['net_text']}"))
    L.append(Q(ingredients_line(spec)))
    for x in allergen_block(spec):
        L.append(Q(x))
    if spec.get("hero_pct_line"):
        L.append(Q(spec["hero_pct_line"]))
    L += [Q(x) for x in spec.get("extra_label_lines") or []]
    L += [Q(x) for x in date_batch_lines(spec)]
    L += [Q(x) for x in standard_lines(spec)]
    if full:
        L.append(Q("贮存条件：" + spec["storage"]))
        m = spec["manufacturer"] if not spec["imported"] else None
        if m:
            L.append(Q(f"生产商：{m['name']}"))
            L.append(Q(f"产地：{spec['origin_shown'] or spec['origin']}"))
        else:
            L.append(Q(f"原产国：{spec['import_info']['origin_country']}"))
            L.append(Q(f"进口商：{spec['import_info']['importer']}"))
    if spec.get("population"):
        L.append(Q(pop_line(spec["population"])))
    return L


def render_ad(spec, promo, g, tampers):
    rng = rng_for("adrender", g["gid"])
    key, subc, _, realism, desc = g["ad_scene"]
    store = g["store"]
    pal = PALETTES[g["palette"]]
    P = []
    rl = "" if (realism == "studio" and "摄影" in desc) else f"{REALISM[realism]}。"
    P.append(f"生成一张{g['aspect']}比例的{desc}，{rl}视觉风格：{AD_STYLE[key]}；海报背景与版式主色调：{pal}（商品包装本身保持下述外观，不改色）。")
    P.append(f"推广商品为虚构品牌{Q(spec['brand'])}的{Q(spec['name'])}（{spec['product_type']}，{spec['net_text']}），商品外观：{spec['visual']}。")
    head = promo["headline"]
    if promo.get("headline_days"):
        head_days = promo["headline_days"]
    else:
        head_days = None
    pb = price_block(promo)
    fcl = front_claim_lines(spec)
    sl = selling_lines(spec)
    date_h = promo_date_text(promo, "headline")
    rules = rules_lines(promo, spec)
    gift_free = promo.get("headline_gift_free")
    regions = []
    # region texts by layout
    top = [Q(store)] if store else [Q(spec["brand"])]
    top.append(Q(head))
    if head_days:
        top.append(Q(head_days))
    top.append(Q(f"活动时间 {date_h}"))
    title = [Q(spec["name"])]
    if spec["headline_extra"]:
        title.append(Q(spec["headline_extra"][0]))
    claim_tags = [Q(x) for x in fcl]
    sell = [Q(x) for x in sl[:3]]
    price = [Q(x) for x in pb]
    if promo.get("gift"):
        gname = promo["gift"].replace("（限量）", "")
        gtxt = f"满{promo['gift_threshold']}元{'免费' if gift_free else ''}送{gname}" + (f"（限量{promo['quota']}份）" if promo.get("quota") else "")
        price.append(Q(gtxt))
    elif promo.get("quota") and promo["type"] == "秒杀":
        price.append(Q(f"限量{promo['quota']}件"))
    info = ad_info_box(spec, full=(key not in ("table_card", "shelf")))
    nutr = nut_block(spec)
    rule_q = [Q(r) for r in rules]
    if key == "ecom_detail":
        P.append("【模块1·头图】顶部为活动横幅" + "、".join(top) + "；下方为商品主图，主图下方为品名" + "、".join(title)
                 + "；价格条（红色底）：" + "、".join(price) + "。")
        P.append("【模块2·核心卖点】图标卡片两行排列（每条一张卡片）：" + "、".join(sell + claim_tags) + "。")
        P.append(f"【模块3·配料表】白底卡片，标题{Q('配料表')}，正文：" + Q(ingredients_line(spec)) +
                 ("；卡片底部：" + QL(allergen_block(spec)) if allergen_block(spec) else "") +
                 (("；" + Q(spec["hero_pct_line"])) if spec.get("hero_pct_line") else "") + "。")
        P.append("【模块4·营养成分】" + nutr + (f" 表格下方：{Q(spec['function_claim'])}" if spec.get("function_claim") else ""))
        params = [Q(f"品名：{spec['name']}"), Q(f"规格：{net_front(spec) if (spec.get('net_shown2') or spec.get('count_shown2')) else spec['net_text']}")]
        params += [Q(x) for x in date_batch_lines(spec)] + [Q(x) for x in standard_lines(spec)]
        params.append(Q("贮存条件：" + spec["storage"]))
        params += [Q(x) for x in producer_lines(spec)[:4]]
        if spec.get("population"):
            params.append(Q(pop_line(spec["population"])))
        P.append("【模块5·产品参数】两列表格（左列字段名、右列内容）逐行为：" + "；".join(params) + "。")
        if spec.get("net_shown2") or spec.get("count_shown2"):
            P.append(f"（注意：头图价格条下方另有一行小字{Q('规格：' + spec['net_text'])}，与参数表规格按给定文字分别呈现。）"
                     if False else "")
        P.append("【模块6·活动规则】浅灰底小字，逐条编号：" + "；".join(rule_q) + "。")
    elif key == "shelf":
        P.append(f"【货架价签】白底价签（位于货架前沿中央）文字：{Q('品名：' + spec['name'])}；{Q('规格：' + spec['net_text'])}；"
                 f"{Q('产地：' + (spec['origin_shown'] or spec['origin']) if not spec['imported'] else '产地：' + spec['import_info']['origin_country'])}；{Q('单位：' + spec['unit_word'] if spec['count']==1 else '单位：箱')}；"
                 f"{Q('零售价：¥' + money(promo['orig']))}；{Q('价格举报电话：12315')}。")
        P.append("【促销爆炸贴】价签上方插着一张红黄色爆炸形促销贴：" + "、".join(top[1:] + price) + "。")
        P.append("【商品】货架上并排摆放6—8件该商品，正面朝外，正面可读文字：" + "、".join(title + claim_tags[:2] + sell[:1]) + (f"、{Q('净含量 ' + net_front(spec))}" if (spec.get('net_shown2') or spec.get('count_shown2')) else "") + "。")
        P.append("【挂卡信息牌】货架侧面挂着一张A5白底商品信息卡，内容：" + "；".join(info) + "；卡片下半部分为" + nutr)
        P.append("【活动规则】爆炸贴下方的细长规则条小字：" + "；".join(rule_q) + "。")
    else:
        lay = rng.choice(["L1", "L2", "L3"]) if key not in ("giftbox_ad",) else "L4"
        if lay == "L1":
            P.append("【顶部（约占画面18%）】" + "、".join(top) + "，门店/品牌名在最上方居左，活动主题大字居中。")
            P.append("【中部主视觉（约35%）】商品实物摄影居中偏右，左侧竖排品名与宣传语：" + "、".join(title) + (("；品名下方的圆角标签：" + "、".join(claim_tags)) if claim_tags else "") + "；卖点短句：" + "、".join(sell) + "。")
            strike = "，原价使用较小字号并带删除线" if any("原价" in x for x in price) else ""
            P.append("【左下（约20%）价格区】醒目大号价格数字：" + "、".join(price) + strike + "。")
            P.append("【右下白底信息框（约22%）】从上到下依次：" + "；".join(info) + "。")
            P.append("【信息框下方或海报右侧窄栏】" + nutr)
            P.append("【最底部通栏小字（较小但清晰）】活动规则：" + "；".join(rule_q) + "。")
        elif lay == "L2":
            P.append("【上半部分】主视觉为商品摄影与食材元素，左上角" + top[0] + "，正中大字" + "、".join(top[1:]) + "；商品下方品名" + "、".join(title) + "。")
            P.append("【中部横条】卖点：" + "、".join(sell) + ("；营养/属性标签：" + "、".join(claim_tags) if claim_tags else "") + "。")
            P.append("【中下部左侧价格牌（倾斜的价格标签样式）】" + "、".join(price) + "。")
            P.append("【中下部右侧“商品信息”卡片】" + "；".join(info) + "。")
            P.append("【底部左侧营养成分小表】" + nutr)
            P.append("【底部右侧活动规则（小字列表）】" + "；".join(rule_q) + "。")
        elif lay == "L3":
            P.append("【顶部横幅】" + "、".join(top) + "。")
            P.append("【左半边】商品大图与宣传：" + "、".join(title) + "；" + "、".join(claim_tags + sell) + "。")
            P.append("【右半边上部价格块】" + "、".join(price) + "。")
            P.append("【右半边中部信息清单】" + "；".join(info) + "。")
            P.append("【右半边下部】" + nutr)
            P.append("【底部细条规则】" + "；".join(rule_q) + "。")
        else:
            P.append("【左侧（约45%）】打开的礼盒俯拍，内部整齐排列多件小包装；左上角" + "、".join(top) + "。")
            P.append("【右上】礼盒名称与宣传：" + "、".join(title) + "；" + "、".join(claim_tags + sell) + "。")
            P.append("【右中价格】" + "、".join(price) + "。")
            P.append("【右下礼盒信息清单】" + "；".join(info) + "。")
            P.append("【底部左侧营养成分表】" + nutr)
            P.append("【底部通栏小字】" + "；".join(rule_q) + "。")
        if spec.get("net_shown2") or spec.get("count_shown2"):
            P.append(f"主视觉商品旁边另有一个圆形角标写{Q(net_front(spec))}。")
    if spec.get("expiry_ink") or (spec.get("inkjet_on") and spec["prod_date"] != spec["prod_date_true"]):
        P.append(f"商品实物图的包装底部可见一处黑色点阵喷码（清晰可读）：{Q(inkjet_text(spec))}。")
    if g["artifacts"]:
        P.append("真实感细节：" + "；".join(PHOTO_ARTIFACTS[a] for a in g["artifacts"]) + "。所有文字区域依然必须清晰锐利、可逐字辨认。")
    P.append(anomaly_note(tampers, "商业广告设计"))
    P.append(text_rules(True))
    return "\n".join(x for x in P if x)
