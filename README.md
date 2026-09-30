# poster_prompts_3000

面向 **富文字 AIGC 图像生成与检测/篡改研究** 的提示词数据集，覆盖宣传海报、食品标签和保健品说明类图像。
共 **3000 条**提示词，可以直接交给 GPT Image 2 / GPT Image 2.5 等文生图模型生成图像。

每条提示词都完整写明了以下内容，尽量不留给模型自由发挥的空间：

- 图像载体、画幅、版式分区和视觉风格；
- 图中必须出现的每一段文字，逐字写在「」内；
- 配料表、营养成分表、价格、活动期限、生产日期、保质期、批号、执行标准号、过敏原等精确字段。

> 所有品牌、公司、机构、商品都是虚构的。地址使用“真实地级市 + 虚构区/街道”，电话、条码、许可证号、批准文号等都是格式正确的虚构编号。数据中的“异常/篡改”只用于研究，不指向任何现实主体。

## 数据集结构

采用 **1000 个基础组 × 3 个版本** 的三联结构：

| variant | 含义 | 条数 |
|---|---|---:|
| `clean` | 正常样本，字段之间逻辑一致 | 1000 |
| `subtle` | 轻微异常：视觉完全正常，只有 1–2 处较隐蔽的文字问题（删掉一个词、改一个数字、调换两项顺序等） | 1000 |
| `strong` | 明显异常：夸大、冲突、缺失或篡改更明显，但画面仍是真实的商业/公益设计 | 1000 |

同一组的三条样本共用同一产品/主题、品牌、场景、构图和视觉风格，只改动关键文字，可以直接用于成对比较（paired comparison）。
篡改文字**不做任何视觉标记**：不圈出、不加警示，而是自然融入原设计。

### 一级类别

| 一级类别 | 基础组 | 提示词 |
|---|---:|---:|
| 食品标签 | 310 | 930 |
| 商业广告 | 240 | 720 |
| 保健品说明 | 160 | 480 |
| 活动宣传 | 150 | 450 |
| 公益海报 | 140 | 420 |
| **合计** | **1000** | **3000** |

二级类别共 100 种，完整列表见 [`poster_prompt_generation_report.md`](poster_prompt_generation_report.md) 第 3 节。

### 篡改类型

共 29 种。其中 5 个重点篡改点如下（一条样本可以同时含多种篡改）：

| 重点篡改点 | tamper_type | 含该类型的样本数 |
|---|---|---:|
| 功效夸大声明 | `efficacy_exaggeration` | 330 |
| 过敏原信息删除 | `allergen_deletion` | 272 |
| 生产日期篡改 | `production_date_tamper` | 272 |
| 保质期篡改 | `shelf_life_tamper` | 305 |
| 配料顺序篡改 | `ingredient_order_tamper` | 301 |

其余扩展类型包括：价格/折扣、活动期限、营养数值/NRV%、营养声称冲突、净含量、执行标准号、批号、批准文号、生产商/产地、警示语删除、适宜人群、产品属性冒充、隐藏付费条件、名额矛盾、流程时间重叠、联系电话、错误健康知识等。完整统计见报告第 5 节。

## 文件说明

```text
.
├── README.md
├── poster_dataset_taxonomy.md            # Phase 1：领域拆分、字段库、法规依据核查、篡改类型库、schema
├── poster_prompt_generation_report.md    # 统计报告（由 src/make_report.py 自动生成）
├── final/
│   ├── poster_prompts_3000.jsonl         # 主数据文件（3000 行）
│   ├── poster_prompts_3000.csv           # 同一数据的 CSV 版（UTF-8 with BOM，Excel 可直接打开）
│   ├── poster_prompts_3000_qa.json       # 自动 QA 结果
│   └── review*/                          # 7 轮人工抽检记录（sample_ids.json + verdict*.jsonl）
├── pilot/
│   ├── poster_prompts_150.jsonl          # Phase 3 pilot（50 组 / 150 条），用当前代码重新生成
│   └── poster_prompts_150_qa.json
├── docs/library_audit/                   # 内容库（131 个原型）逐条审计记录
└── src/                                  # 生成器、内容库、QA 与统计脚本（仅依赖 Python 标准库）
```

## 数据字段（JSONL 每行）

| 字段 | 说明 |
|---|---|
| `id` | 提示词 ID，`P000001`–`P003000` |
| `group_id` | 基础组 ID，`G0001`–`G1000`，每组正好 clean/subtle/strong 各 1 条 |
| `variant` | `clean` / `subtle` / `strong` |
| `super_category` / `sub_category` | 一级 / 二级类别 |
| `scene_type` / `carrier` / `realism` | 场景描述 / 图像载体 / 真实感（`flat` 平面稿、`studio` 棚拍、`scene` 实景、`phone` 手机实拍） |
| `product_type` / `product_or_title` / `brand_or_organizer` | 商品类型 / 品名或活动标题 / 虚构品牌或主办方 |
| `visual_style` / `layout` / `aspect_ratio` / `text_density` | 视觉风格 / 版式模板 / 画幅 / 文本密度 |
| `required_fields` | 图中必须出现的字段 |
| `tamper_types` / `tampered_fields` | 篡改类型 / 被篡改字段（clean 为空） |
| `tamper_details` | 用自然语言写明的篡改真值：改了什么、原值是什么、与哪里冲突 |
| `difficulty` | clean 为 `reference`，其余标注难度 |
| `single_image_detectable` | 仅看单张图能否发现矛盾（`false` 多为纯删除，只有与同组 clean 对照才能发现）；clean 为 `null` |
| `source_archetype` | 生成所用的内容原型 ID |
| `prompt` | 最终生图提示词（中文） |

**评测建议：**

- 做单图异常检测时，按 `single_image_detectable` 拆开报告；
- 做成对比较时，用 `group_id` 对齐三联样本；
- `tamper_details` 可以直接作为定位与解释任务的参考答案（ground truth）。

## 使用示例

```python
import json
rows = [json.loads(l) for l in open("final/poster_prompts_3000.jsonl", encoding="utf-8")]
g = [r for r in rows if r["group_id"] == "G0001"]
for r in g:
    print(r["id"], r["variant"], r["tamper_types"], r["tamper_details"])
# 把 r["prompt"] 原样发给图像模型即可，不需要额外拼接
```

## 复现

仅依赖 Python 3.11 标准库，无第三方包。在仓库根目录运行：

```bash
python src/validate_libs.py                                   # 内容库自检（配料百分比、营养数值、声称条件、过敏原映射等）
python src/generate.py --groups 50   --out pilot              # pilot：50 组 / 150 条
python src/qa.py pilot/poster_prompts_150.jsonl --sample 30
python src/generate.py --groups 1000 --out final              # 全量：1000 组 / 3000 条
python src/qa.py final/poster_prompts_3000.jsonl --sample 100 # 结构、模板残留、字段完整度、三联一致性、语义一致性
python src/qa_round2_checks.py                                # 针对人工抽检发现的缺陷类别写的全量回归检查
python src/qa_round4_checks.py
python src/qa_round5_checks.py
python src/make_report.py                                     # 重新生成统计报告
```

生成过程是确定性的：每个随机数生成器都由固定种子和组 ID 派生。在同一平台上重新运行会得到逐字节相同的文件，SHA-256 见 [`SHA256SUMS.txt`](SHA256SUMS.txt)。在 Linux/macOS 上换行符是 LF，文件哈希会不同，但逐行解析后的内容一致。

## 质量控制

- **自动 QA**：3000 行全部可解析，ID 唯一，1000 组三联完整；没有模板残留（TODO、XXXX、未闭合括号等）；没有完全重复的 prompt。clean 样本在以下各项上均无违规：
  - 日期：保质期推算、批号与日期、星期与日期；
  - 营养表：NRV%、能量与三大营养素是否一致、营养声称条件；
  - 其他：过敏原与配料是否一致、流程时间是否冲突、促销期是否超出保质期。
- **人工抽检**：共 7 轮。每轮从当时最新的完整 3000 条中随机抽 100 条，由 4 个相互独立的 LLM 审阅代理逐条判断“能否直接生图 / 是否真实 / 篡改是否成立、clean 是否自洽”。每发现一类缺陷，都回到生成器或内容库修根本原因，再全量重新生成。major 缺陷数依次为 24 → 7 → 9 → 5 → 7 → 2 → 1，第 7 轮修复后又全量回归检查。详见报告第 9 节。
- **法规口径**：营养声称条件、0 界限值、NRV、致敏物质、保健功能目录用语等，依据见 taxonomy 第 6 节。无法确认的规则一律标注为 *dataset-designed anomaly*，不作为法律结论。

## 已知局限

- 部分 `subtle` 样本（`single_image_detectable=false`）无法仅凭单图判定。
- 活动宣传类的长流程表、Very High 密度的实拍风小字，GPT Image 渲染时可能漏行或不可读，出图后建议用 OCR 复核。
- 进口食品中文补充标签的样本较少。
- 内容由程序化生成器加人工设计的内容库产生，同一原型内的样本共享法定标签骨架（相似度见报告第 7 节）。
- `final/review*/` 中的审阅意见针对的是**当轮**版本；之后已修复并重新生成，所以早期轮次的问题不代表最终版本。各轮送审的 prompt 快照属于中间版本，未上传。
