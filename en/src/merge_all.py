"""Merge the Chinese (final/poster_prompts_3000.jsonl) and English (en/final/poster_prompts_en_1002.jsonl) parts into
merged/poster_prompts_all_4002.jsonl/.csv with one unified schema.  Usage (repo root): python en/src/merge_all.py"""
import csv
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
KEY = {"食品标签": "food_label", "商业广告": "commercial_ad", "保健品说明": "supplement", "活动宣传": "event", "公益海报": "public_service",
       "Food label": "food_label", "Commercial ad": "commercial_ad", "Supplement": "supplement", "Event": "event",
       "Public-service poster": "public_service"}
COLS = ["id", "group_id", "variant", "lang", "category_key", "super_category", "sub_category", "country", "region", "scene_type",
        "product_type", "visual_style", "layout", "aspect_ratio", "text_density", "required_fields", "tamper_types", "tampered_fields",
        "tamper_details", "difficulty", "single_image_detectable", "carrier", "realism", "brand_or_organizer", "product_or_title",
        "source_archetype", "prompt"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    zh = load(os.path.join(ROOT, "final", "poster_prompts_3000.jsonl"))
    en = load(os.path.join(ROOT, "en", "final", "poster_prompts_en_1002.jsonl"))
    out = []
    for r in zh:
        x = dict(r, lang="zh", country="CN", region="CN")
        out.append(x)
    out += [dict(r) for r in en]
    for x in out:
        x["category_key"] = KEY[x["super_category"]]
    ids = [x["id"] for x in out]
    gids = {x["group_id"] for x in out}
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(gids) * 3 == len(out), "groups not triplets"
    os.makedirs(os.path.join(ROOT, "merged"), exist_ok=True)
    base = os.path.join(ROOT, "merged", "poster_prompts_all_%d" % len(out))
    with open(base + ".jsonl", "w", encoding="utf-8", newline="\n") as f:
        for x in out:
            f.write(json.dumps({c: x.get(c) for c in COLS}, ensure_ascii=False) + "\n")
    with open(base + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for x in out:
            w.writerow([json.dumps(x.get(c), ensure_ascii=False) if isinstance(x.get(c), list) else ("" if x.get(c) is None else x.get(c)) for c in COLS])
    print("merged", len(zh), "zh +", len(en), "en =", len(out), "rows,", len(gids), "groups ->", base)


if __name__ == "__main__":
    main()
