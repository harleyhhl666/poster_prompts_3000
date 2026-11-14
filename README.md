# poster_prompts_3000

面向 **富文字 AIGC 图像生成与检测/篡改研究** 的提示词数据集，覆盖宣传海报、食品标签和保健品说明类图像。
共 **4002 条**提示词，可以直接交给 GPT Image 2 / GPT Image 2.5 等文生图模型生成图像：

| 部分 | 语言 / 场景 | 三联组 | 提示词 | ID 范围 | 目录 |
|---|---|---:|---:|---|---|
| 中文部分 | 中文，中国大陆 | 1000 | 3000 | `P000001`–`P003000` | `final/` |
| 英文部分 | 英文，欧洲（EU/EEA、英国、瑞士）+ 北美（美国、加拿大） | 334 | 1002 | `P003001`–`P004002` | `en/final/` |
| 合并文件 | 两部分统一字段 | 1334 | 4002 | — | `merged/` |

英文部分按需求是 1000 条。因为每组固定 3 条，这里取 334 组 = 1002 条，保证每个三联组都完整。

每条提示词都完整写明了以下内容，尽量不留给模型自由发挥的空间：

- 图像载体、画幅、版式分区和视觉风格；
- 图中必须出现的每一段文字，逐字写在「」内（提示词中注明括号本身不画出）；
- 配料表、营养成分表、价格、活动期限、生产日期、保质期、批号、过敏原等精确字段。

> 所有品牌、公司、机构、商品都是虚构的。中文部分的地址使用“真实地级市 + 虚构区/街道”；英文部分使用真实城市，邮编和电话区号符合当地格式，街道取当地常见街名，门牌和公司地址都是虚构的；北美电话号码取自影视专用的 555-01xx 号段。条码校验位正确，但编号是虚构的。数据中的“异常/篡改”只用于研究，不指向任何现实主体。

## 数据集结构

两部分都采用 **基础组 × 3 个版本** 的三联结构：

| variant | 含义 | 中文 | 英文 |
|---|---|---:|---:|
| `clean` | 正常样本，字段之间逻辑一致 | 1000 | 334 |
| `subtle` | 轻微异常：视觉完全正常，只有 1–2 处较隐蔽的文字问题（删掉一个词、改一个数字、调换两项顺序等） | 1000 | 334 |
| `strong` | 明显异常：夸大、冲突、缺失或篡改更明显，但画面仍是真实的商业/公益设计 | 1000 | 334 |

同一组的三条样本共用同一产品/主题、品牌、场景、构图和视觉风格，只改动关键文字，可以直接用于成对比较（paired comparison）。
篡改文字**不做任何视觉标记**：不圈出、不加警示，而是自然融入原设计。

### 一级类别

| 一级类别 | `category_key` | 中文组 / 条 | 英文组 / 条 |
|---|---|---:|---:|
| 食品标签 / Food label | `food_label` | 310 / 930 | 104 / 312 |
| 商业广告 / Commercial ad | `commercial_ad` | 240 / 720 | 80 / 240 |
| 保健品说明 / Supplement | `supplement` | 160 / 480 | 53 / 159 |
| 活动宣传 / Event | `event` | 150 / 450 | 50 / 150 |
| 公益海报 / Public-service poster | `public_service` | 140 / 420 | 47 / 141 |
| **合计** | | **1000 / 3000** | **334 / 1002** |

二级类别：中文 100 种，英文 82 种。完整列表分别见 [`poster_prompt_generation_report.md`](poster_prompt_generation_report.md) 和 [`en/poster_prompt_generation_report_en.md`](en/poster_prompt_generation_report_en.md) 第 3 节。

### 英文部分的地区与标签规则

- 覆盖 33 个国家。按组计：美国 101、欧盟/EEA/瑞士 90、英国 82、爱尔兰 50、加拿大 11。
- **包装食品和保健品标签**只放在“只印英文就合法”的市场：英国、爱尔兰、马耳他、美国。依据是 EU 1169/2011 第 15 条（标签须使用当地易懂的语言）。加拿大要求双语标签，所以只用于活动和公益海报。为了覆盖欧洲其他国家，产品产地分布在意大利、波兰、挪威等国，由当地公司进口。
- **欧盟/英国标签**：配料按含量降序，过敏原在配料中用大写强调；名称或宣传中提到的配料标注 QUID 百分比；营养表给出每 100 g、每份和 %RI；钠以盐计。营养声称按 1924/2006 附件的条件校验，健康声称逐字取自 432/2012 清单。
- **美国标签**：Nutrition Facts / Supplement Facts 按 FDA 规则修约并计算 %DV，使用 CONTAINS 过敏原声明、`NET WT x OZ (g)`、MM/DD 日期和华氏度，并做了美式拼写转换。
- 在非英语国家投放的广告、活动、公益海报，提示词里会用一句话交代为什么用英文（例如面向国际学生、外籍社区）。

### 篡改类型

两部分共用同一套篡改类型库，各 29 种。其中 5 个重点篡改点如下（一条样本可以同时含多种篡改）：

| 重点篡改点 | tamper_type | 中文样本数 | 英文样本数 |
|---|---|---:|---:|
| 功效夸大声明 | `efficacy_exaggeration` | 330 | 120 |
| 过敏原信息删除 | `allergen_deletion` | 272 | 97 |
| 生产日期篡改 | `production_date_tamper` | 272 | 90 |
| 保质期篡改 | `shelf_life_tamper` | 305 | 94 |
| 配料顺序篡改 | `ingredient_order_tamper` | 301 | 89 |

其余扩展类型包括：价格/折扣、活动期限、营养数值、营养声称冲突、净含量、批号、生产商/产地、警示语删除、适宜人群、产品属性冒充、隐藏付费条件、名额矛盾、流程时间重叠、联系电话、错误健康知识、信息来源冒用等。中文部分另有执行标准号、批准文号等中国特有字段。完整统计见两份报告的第 5 节。

## 文件说明

```text
.
├── README.md
├── poster_dataset_taxonomy.md            # 中文部分 Phase 1：领域拆分、字段库、法规依据核查、篡改类型库、schema
├── poster_prompt_generation_report.md    # 中文部分统计报告（src/make_report.py 自动生成）
├── final/                                # 中文部分
│   ├── poster_prompts_3000.jsonl / .csv  # 主数据（CSV 为 UTF-8 with BOM，Excel 可直接打开）
│   ├── poster_prompts_3000_qa.json       # 自动 QA 结果
│   └── review*/                          # 7 轮人工抽检记录
├── pilot/                                # 中文 pilot（50 组 / 150 条）
├── docs/library_audit/                   # 中文内容库（131 个原型）逐条审计记录
├── src/                                  # 中文生成器、内容库、QA 与统计脚本
├── en/                                   # 英文部分
│   ├── taxonomy_en.md                    # 地区与配额、欧盟/英国/美国标签规则（附原文出处）、篡改类型库，均在生成前冻结
│   ├── poster_prompt_generation_report_en.md
│   ├── refs/                             # eu432_claims.json（432/2012 健康声称清单）、facts_whitelist.md（公益海报数字及出处）
│   ├── final/
│   │   ├── poster_prompts_en_1002.jsonl / .csv
│   │   ├── poster_prompts_en_1002_qa.json
│   │   └── review1–5/                    # 5 轮人工抽检记录（RUBRIC.md、sample_ids.json、verdict*.jsonl）
│   ├── pilot/                            # 英文 pilot（50 组 / 150 条）
│   └── src/                              # 英文生成器、内容库（parts/）、validate_libs.py、qa_en.py、merge_all.py
└── merged/
    └── poster_prompts_all_4002.jsonl / .csv   # 中英合并，统一字段
```

## 数据字段（JSONL 每行）

| 字段 | 说明 |
|---|---|
| `id` | 提示词 ID，中文 `P000001`–`P003000`，英文 `P003001`–`P004002` |
| `group_id` | 基础组 ID，中文 `G0001`–`G1000`，英文接着往后编；每组正好 clean/subtle/strong 各 1 条 |
| `variant` | `clean` / `subtle` / `strong` |
| `lang` / `country` / `region` | 英文部分和合并文件才有。`lang` 为 `zh` 或 `en`；`country` 为 ISO 国家代码；`region` 为 `CN` / `US` / `CA` / `UK` / `IE` / `EU` |
| `category_key` | 仅合并文件有，一级类别的语言无关键名（见上表） |
| `super_category` / `sub_category` | 一级 / 二级类别（中文部分为中文名，英文部分为英文名） |
| `scene_type` / `carrier` / `realism` | 场景描述 / 图像载体 / 真实感（`flat` 平面稿、`studio` 棚拍、`scene` 实景、`phone` 手机实拍） |
| `product_type` / `product_or_title` / `brand_or_organizer` | 商品类型 / 品名或活动标题 / 虚构品牌或主办方 |
| `visual_style` / `layout` / `aspect_ratio` / `text_density` | 视觉风格 / 版式模板 / 画幅 / 文本密度 |
| `required_fields` | 图中必须出现的字段 |
| `tamper_types` / `tampered_fields` | 篡改类型 / 被篡改字段（clean 为空） |
| `tamper_details` | 用自然语言写明的篡改真值：改了什么、原值是什么、与哪里冲突 |
| `difficulty` | clean 为 `reference`，其余标注难度 |
| `single_image_detectable` | 仅看单张图能否发现矛盾（`false` 多为纯删除，只有与同组 clean 对照才能发现）；clean 为 `null` |
| `source_archetype` | 生成所用的内容原型 ID |
| `prompt` | 最终生图提示词（中文部分为中文，英文部分为英文） |

**评测建议：**

- 做单图异常检测时，按 `single_image_detectable` 拆开报告；
- 做成对比较时，用 `group_id` 对齐三联样本；
- `tamper_details` 可以直接作为定位与解释任务的参考答案（ground truth）；
- 跨语言实验用合并文件里的 `lang` 和 `category_key` 分组。

## 使用示例

```python
import json
rows = [json.loads(l) for l in open("merged/poster_prompts_all_4002.jsonl", encoding="utf-8")]
en = [r for r in rows if r["lang"] == "en"]
g = [r for r in en if r["group_id"] == en[0]["group_id"]]
for r in g:
    print(r["id"], r["variant"], r["country"], r["tamper_types"], r["tamper_details"])
# 把 r["prompt"] 原样发给图像模型即可，不需要额外拼接
```

## 复现

仅依赖 Python 3.11+ 标准库，无第三方包。在仓库根目录运行：

```bash
# 中文部分
python src/validate_libs.py
python src/generate.py --groups 1000 --out final
python src/qa.py final/poster_prompts_3000.jsonl --sample 100
python src/qa_round2_checks.py && python src/qa_round4_checks.py && python src/qa_round5_checks.py
python src/make_report.py

# 英文部分
python en/src/validate_libs.py                                   # 内容库自检（配料、营养、声称条件、过敏原、真实品牌黑名单等）
python en/src/generate_en.py --groups 50  --out en/pilot
python en/src/generate_en.py --groups 334 --out en/final
python en/src/qa_en.py en/final/poster_prompts_en_1002.jsonl     # 结构 + 语义一致性 + 各轮审阅缺陷的回归检查
python en/src/make_report_en.py

# 合并
python en/src/merge_all.py                                       # -> merged/poster_prompts_all_4002.jsonl/.csv
```

生成过程是确定性的：每个随机数生成器都由固定种子和组 ID 派生。在同一平台上重新运行会得到逐字节相同的文件，SHA-256 见 [`SHA256SUMS.txt`](SHA256SUMS.txt)。在 Linux/macOS 上换行符是 LF，文件哈希会不同，但逐行解析后的内容一致。

## 质量控制

**中文部分**

- **自动 QA**：3000 行全部可解析，ID 唯一，1000 组三联完整；没有模板残留（TODO、XXXX、未闭合括号等）；没有完全重复的 prompt。clean 样本在以下各项上均无违规：
  - 日期：保质期推算、批号与日期、星期与日期；
  - 营养表：NRV%、能量与三大营养素是否一致、营养声称条件；
  - 其他：过敏原与配料是否一致、流程时间是否冲突、促销期是否超出保质期。
- **人工抽检**：共 7 轮。每轮从当时最新的完整 3000 条中随机抽 100 条，由 4 个相互独立的 LLM 审阅代理逐条判断“能否直接生图 / 是否真实 / 篡改是否成立、clean 是否自洽”。每发现一类缺陷，都回到生成器或内容库修根本原因，再全量重新生成。major 缺陷数依次为 24 → 7 → 9 → 5 → 7 → 2 → 1，第 7 轮修复后又全量回归检查。详见报告第 9 节。
- **法规口径**：营养声称条件、0 界限值、NRV、致敏物质、保健功能目录用语等，依据见 taxonomy 第 6 节。无法确认的规则一律标注为 *dataset-designed anomaly*，不作为法律结论。

**英文部分**

- **自动 QA**（`en/src/qa_en.py`）：1002 行，0 个错误。检查内容包括三联结构、tamper_details 引用的文字确实出现在 prompt 里、日期/批号/星期推算、欧盟 %RI 与能量、美国 %DV 与 FDA 修约、过敏原与配料一致、营养声称条件，以及按审阅缺陷类别补写的回归检查。内容库由 `validate_libs.py` 对照 611 个真实品牌的黑名单检查；对最终 1002 条「」内文字再扫描一遍，没有命中。clean 组之间的 6-gram Jaccard 相似度中位数为 0–0.03。
- **人工抽检**：共 5 轮，方法同中文部分（每轮新抽 100 条，4 个审阅代理，评分标准见 `en/final/review*/RUBRIC.md`）。major 缺陷数依次为 28 → 14 → 10 → 9 → 8。
- **第 4、5 轮之后**：没有再做第 6 轮人工抽检，第 4、5 轮发现的 11 类缺陷改用全量回归检查验证，命中数从修复前（第 4 轮送审版本）的 59 处降到 0。修复内容见英文报告第 9 节，主要包括：
  - 加拿大海报不再出现只有华氏度或引用美国机构的情况；
  - 多件装的每份重量与单件一致；
  - 美国饮料按 8 fl oz 计一份；
  - 补剂宣传的“N 个月用量”与粒数和日剂量一致；
  - 免预约活动不再写“限 N 人”；
  - 欧盟补剂的过敏原删除会同时去掉大写强调。
- **法规口径**：欧盟/英国/美国规则都核对过法规原文，所依据的条例和条款（如 Reg (EU) 1169/2011、1924/2006、432/2012、21 CFR 101.9/101.36）见 `en/taxonomy_en.md`。公益海报中的每个数字都必须出自 `en/refs/facts_whitelist.md`，并且只能用于白名单写明的地区。

## 已知局限

- 部分 `subtle` 样本（`single_image_detectable=false`，中文若干、英文 30 条）无法仅凭单图判定。
- 活动宣传类的长流程表、Very High 密度的实拍风小字，GPT Image 渲染时可能漏行或不可读，出图后建议用 OCR 复核。
- 中文部分：进口食品中文补充标签的样本较少。
- 英文部分：
  - 加拿大只有活动和公益海报（11 组）。去掉北美通用的华氏度事实后，加拿大公益海报只剩 3 个主题。“孕期食品安全”“烧烤安全”两个美国二级类别在本版中为 0 组。
  - 第 5 轮审阅中仍有少量 minor 问题：多语种零售商名与所在国不匹配、个别风格与配色描述冲突、欧盟婴儿食品仍使用成人 %RI 列。
  - 第 4、5 轮修复后只做了全量回归检查，没有再做一轮新的人工抽检，所以没有修复后的 major 率。
- 内容由程序化生成器加人工设计的内容库产生，同一原型内的样本共享法定标签骨架（相似度见两份报告第 7 节）。
- `review*/` 中的审阅意见针对的是**当轮**版本，之后已修复并重新生成，所以早期轮次的问题不代表最终版本。各轮送审的 prompt 快照属于中间版本，未上传。
