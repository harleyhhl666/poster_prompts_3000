"""Round-5 regression checks (whole file)."""
import sys, os, json, re, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_review_checks import quoted
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "final/poster_prompts_3000.jsonl", encoding="utf-8")]
C = collections.Counter(); EX = collections.defaultdict(list)


def hit(k, r):
    C[k] += 1
    if len(EX[k]) < 3:
        EX[k].append(r["id"])


def tm(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)


def pd(s):
    for f in ("%Y年%m月%d日", "%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(s.strip(), f).date()
        except ValueError:
            pass


for r in rows:
    p = r["prompt"]; t = "\n".join(quoted(p))
    # agenda overlap truth
    slots = re.findall(r"「(\d{1,2}:\d{2})—(\d{1,2}:\d{2})｜", p)
    overl = any(tm(slots[i][0]) < tm(slots[i - 1][1]) for i in range(1, len(slots)))
    if "agenda_time_conflict" in r["tamper_types"] and not overl:
        hit("agenda_tamper_no_overlap", r)
    if "agenda_time_conflict" not in r["tamper_types"] and overl:
        hit("agenda_untagged_overlap", r)
    # daily hours vs agenda (events)
    mh = re.search(r"活动时间：[^」]*?(\d{1,2}:\d{2})—(\d{1,2}:\d{2})", t)
    if r["super_category"] == "活动宣传" and mh and slots and "agenda_time_conflict" not in r["tamper_types"]:
        if tm(slots[0][0]) < tm(mh.group(1)) or tm(slots[-1][1]) > tm(mh.group(2)):
            hit("hours_vs_agenda", r)
    # deletion tamper leaves near duplicate
    for d in r["tamper_details"]:
        m = re.search(r"删除了(?:重点提示|免责/风险提示|注意事项中删除了)?「([^」]+)」", d) or re.search(r"注意事项中删除了「([^」]+)」", d)
        if m and ("warning_deletion" in r["tamper_types"]):
            core = re.sub(r"[，。、；！\s请]", "", m.group(1))
            tt = t.replace("保健食品不是药物，不能代替药物治疗疾病。", "") if "注意事项" in d else t
            if len(core) >= 6 and any(core[i:i + 6] in re.sub(r"[，。、；！\s请]", "", tt) for i in range(len(core) - 5)):
                hit("deleted_text_still_present", r)
    # promo end after expiry (clean ads)
    if r["super_category"] == "商业广告" and r["variant"] == "clean":
        me = re.search(r"保质期至：([^」]+)」", p)
        ma = re.search(r"「活动时间：(\d{4})年(\d{1,2})月(\d{1,2})日(?:至(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日)?", p)
        if me and ma:
            exp = pd(me.group(1))
            y = int(ma.group(4) or ma.group(1))
            end = dt.date(y, int(ma.group(5) or ma.group(2)), int(ma.group(6) or ma.group(3)))
            if exp and end > exp:
                hit("promo_after_expiry", r)
    # soy sauce wheat
    ing = re.search(r"(?:配料|原料)[：】]([^」]+)", t)
    al = re.search(r"(?:过敏原信息|致敏物质提示|食物过敏原提示)：[^」]*", t)
    if r["variant"] == "clean" and ing and al and "酱油" in ing.group(1) and "小麦" not in al.group(0) and "麸质" not in al.group(0):
        hit("soy_sauce_no_wheat", r)
    # CNY-day events not about CNY
    for m in re.finditer(r"(\d{4})年(\d{1,2})月(\d{1,2})日", t):
        d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if r["super_category"] in ("活动宣传", "公益海报") and dt.date(2027, 2, 4) <= d <= dt.date(2027, 2, 13) and not any(k in p for k in ["年货", "春节", "新春"]):
            hit("event_on_cny", r)
            break
    if re.search(r"胶囊标签「[^」]*」与「限\d+名」", p) and re.search(r"每场限\d+组家庭", t):
        hit("quota_unit", r)
print(json.dumps(C, ensure_ascii=False)); print(json.dumps(EX, ensure_ascii=False))
