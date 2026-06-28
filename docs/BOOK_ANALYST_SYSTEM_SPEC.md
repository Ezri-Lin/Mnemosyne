# Mnemosyne Book Analyst System Spec

> 本文是 Book Analyst 的业务核心规范。后续 skill、HTML 模板、JSON 数据、Obsidian 笔记、数据库落库、页面改版都必须服从这里的职责边界。

## 1. 产品定义

Book Analyst 不是普通书摘，也不是漂亮的静态网页。它的核心是：

**让 AI 像老师备课一样先读书、拆书、划重点、建立证据链，然后把这本书变成一个可导航、可追溯、可继续对话、可沉淀到个人知识库的读书系统。**

用户不一定从第一页读到最后一页。用户可以先通过全书结构理解这本书，再按主题、章节、证据、概念或个人问题进入原书精读。

### 1.1 不可变业务目标

- 读书前：用户先获得全书地图、重点章节、核心概念、推荐阅读顺序和为什么读。
- 读书中：用户可以从主题、概念、证据、章节关系进入原文，定位值得精读的部分。
- 读书后：用户可以和 AI 继续讨论，把真正有价值的理解保存到 Markdown、数据库或 Obsidian 双链知识库。
- 展示层：尽量使用图形、卡片、表格、矩阵、时间线、因果链、概念网、证据板表达结构，避免纯文字长墙。
- 来源层：任何作者观点、原文引用、案例、研究证据都必须可追溯到章节或页码范围。
- 解释层：AI 的理解必须和作者原文、用户个人理解分开标注。

### 1.2 非目标

- 不做单纯摘要站。
- 不在前端展示“组件拼装谱系”或后台生成逻辑。
- 不编造书籍标签、分类、阅读模式、证据、引用或用户个人价值点。
- 不让 Mnemosyne Flask 服务直接承担 AI 分析。
- 不为了设计而设计。视觉、组件和动效必须服务于读书导航。

### 1.3 产品形态定位

Book Analyst 的主体不是一个传统 Web 服务，而是一套 **AI Agent 阅读书籍的方法论 skill**，以及这套 skill 生成的静态可视化前端产物。

核心产物是：

```text
Skill Methodology
  规定 AI Agent 如何拆书、筛章节、建主题、找证据、生成 JSON/Markdown/HTML。

Structured Content
  由 AI Agent 生成的 book.json、chapters/*.json、themes/*.json、evidence/*.json、notes/*.md。

Static Visual Artifact
  由固定组件和固定样式渲染出的 web/index.html 与 web/chapters/*.html。
```

因此，Book Analyst 可以运行成多种形态：

- 本地 Flask 服务：适合本地 vault、上传、调试、预览。
- 纯静态站点：适合 GitHub Pages、Cloudflare Pages、Netlify 等部署。
- GitHub 仓库产物：Agent 在本地或远程生成 JSON/Markdown/HTML，提交到仓库后由静态站点读取。
- Obsidian 辅助视图：Markdown 是长期知识库，HTML 是可视化阅读导航。

唯一需要后端的部分是“上传书籍并提取基础元信息”：如封面、作者、年份、语言、source 文件保存位置、书籍元数据保存位置。除此之外，书籍分析和页面展示都应尽量保持静态、可复制、可版本管理。

## 2. 系统分层

```text
AI Agent + book-analyst skill
  核心。负责拆书、章节分级、主题聚类、证据链、页面数据生成。

book-to-webpage component library
  提供 base.html、主题 token、可交互组件范式。

Static Web Artifact
  web/index.html、web/chapters/*.html、组件 CSS/JS、主题 token。

Golden House / Obsidian Vault / Git Repository
  保存原书、JSON、Markdown、生成 HTML、读后笔记、双链知识。

Optional Metadata Backend
  保存书籍元数据、封面、上传记录、阅读状态、解析状态。

Mnemosyne Flask App
  当前本地实现。负责图书馆、上传、状态、读取 web/index.html 和章节 HTML。
```

### 2.1 展示层职责：Mnemosyne

Mnemosyne 只做“存书 + 展示”：

- 图书馆海报墙。
- 上传书籍文件。
- 维护书籍元数据、阅读状态、解析状态。
- 读取 `vault/.../<Book>/web/index.html`。
- 读取 `vault/.../<Book>/web/chapters/*.html`。
- 无解析内容时显示未解析提示。

Mnemosyne 不做：

- 不调用 LLM 分析书。
- 不拆章节。
- 不生成 AI 摘要。
- 不替用户写永久笔记。

未来如果迁移为纯静态站点，Mnemosyne 的大部分职责可以被静态托管替代；只需保留一个可选的元数据写入通道，用于上传、封面提取、source 文件存放和基础书籍信息保存。

### 2.2 分析层职责：AI Agent Skill

分析层负责：

- 提取原文。
- 识别章节结构。
- 只按需读取章节，避免一次性全书读入导致上下文漂移。
- 章节分级。
- 主题聚类。
- 证据链生成。
- 组件数据 JSON 生成。
- HTML / Markdown / 数据库写入。
- 读后对话中的个人理解沉淀。

分析层是系统真正的“业务引擎”。前端不负责理解书，前端只渲染分析层输出的结构化内容。

### 2.3 持久化层职责

建议把产物分层保存：

```text
<Book>/
  source/
    原书文件、OCR 文本、提取后的 full_text

  analysis/
    book.json
    chapters/*.json
    themes/*.json
    concepts/*.json
    evidence/*.json

  notes/
    Phase 1 - God's-eye View.md
    Phase 2 - Chapter Value Grading.md
    Reading Guide.md
    Personal Reflections.md

  web/
    index.html
    chapters/chNN-slug.html

  memory/
    personal-value.json
    permanent-note-candidates.md
    backlinks.json
```

初期可以不全部落库，但数据语义必须从一开始分清楚。

### 2.4 静态优先原则

除上传和元数据写入外，系统应优先保持静态产物形态：

- JSON / Markdown 是内容源。
- HTML 是可视化结果。
- CSS / JS 是固定组件和交互。
- Git 可以作为版本管理和同步层。
- 页面不依赖运行时 AI 服务才能阅读。

这保证用户多年后打开生成结果，仍然能查看当时的 AI 读书笔记、证据链和个人思考。

## 3. 首次生成配置向导

第一次对某个项目库使用 Book Analyst 时，skill 应该先确认配置，而不是直接生成页面。

### 3.1 必选配置

```json
{
  "projectLibraryRoot": "当前项目库或 vault 根目录",
  "bookSourceRoot": "书籍原文来源目录",
  "analysisOutputRoot": "AI 结构化分析数据保存目录",
  "webOutputRoot": "HTML 页面输出目录",
  "notesOutputRoot": "Markdown 笔记输出目录",
  "knowledgeSink": "读后知识点最终保存位置",
  "metadataStore": "书籍基础元信息保存位置"
}
```

### 3.2 可选配置

```json
{
  "language": "zh-CN",
  "theme": "warm-paper",
  "density": "balanced",
  "quotePolicy": "short-with-source",
  "personalization": "phase-4-only",
  "chapterGeneration": "value-density>=4",
  "sourceTrace": true
}
```

### 3.3 配置含义

| 配置 | 含义 |
| --- | --- |
| `language` | 页面和笔记输出语言。可支持中文、英文、双语。 |
| `theme` | 使用 book-to-webpage 的主题 token，如 `warm-paper`、`minimal`、`dark`、`ink-wash`。 |
| `density` | 信息密度。初期建议 `balanced`，允许更多内容但避免拥挤。 |
| `personalization` | Phase 1-3 默认不加入用户个人价值判断；Phase 4 才允许结合用户历史记忆。 |
| `chapterGeneration` | 初期只为高价值章节生成详情页，避免无意义页面膨胀。 |
| `sourceTrace` | 每个内容块必须有出处。 |
| `metadataStore` | 保存封面、作者、年份、语言、source 路径、阅读状态、解析状态。可为 SQLite、JSON 文件、GitHub 仓库或其他后端。 |

## 4. 用户完整流程

### 4.1 开始前

1. 用户在图书馆上传书籍，或把书放入 vault/source。
2. 用户对支持 skill/workflow 的 AI Agent 说“帮我阅读这本书”。
3. skill 检查项目配置。
4. skill 估算提取和分析成本。
5. 用户确认后开始分析。

上传流程只负责基础元信息：

- 保存原书文件。
- 提取或上传封面。
- 识别书名、作者、年份、语言、文件格式。
- 写入 `metadataStore`。
- 将书标记为 `not-parsed` 或 `queued`。

上传流程不直接生成书籍分析。真正的阅读、拆解、证据链和页面数据由 AI Agent 在 skill 流程中完成。

### 4.2 生成中

1. 提取全文。
2. 识别章节。
3. 生成全书上帝视角。
4. 对每章打价值分。
5. 只深读高价值章节和关键主题。
6. 生成主题聚类、概念索引、证据链。
7. 生成 Markdown 笔记。
8. 生成书籍导航页和章节详情页。
9. 验证 HTML 可点击、可追溯、无空块。

### 4.3 用户使用中

用户打开图书馆，点击书籍进入书籍导航页。

推荐路径：

```text
先看一句话总论
→ 看主题聚类地图
→ 看章节热力与推荐理由
→ 选择一个主题或问题
→ 看相关概念和证据
→ 进入章节详情页
→ 回原文精读
→ 和 AI 继续追问
```

用户可以不用按书籍原章节顺序阅读，而是按主题和证据路径阅读。

### 4.4 读后沉淀

用户读完或阶段性读完后，可以继续问：

- 这章对我有什么价值？
- 这个概念和我之前关心的问题有什么关系？
- 哪些内容值得保存到 Obsidian？
- 帮我整理成永久笔记候选。
- 这个观点有什么反例或局限？

读后产物应保存为：

- `myReflection`：用户自己的理解。
- `aiSynthesis`：AI 结合上下文后的解释。
- `sourceRefs`：对应原书证据。
- `knowledgeLinks`：Obsidian 双链或数据库知识点关联。

## 5. 图书馆页规范

图书馆页负责管理“多本书”，不是解释单本书。

### 5.1 必须保留的功能

- 海报墙 / 列表切换。
- 上传按钮。
- 搜索。
- 阅读状态筛选：completed / reading / to-read / paused。
- 解析状态筛选：parsed / not-parsed。
- 语言筛选。
- 排序。
- 封面和基础元数据。
- 点击进入书籍页。

### 5.2 不应该加入的内容

- 不加入没有真实数据来源的书籍领域筛选。
- 不在图书馆页解释书籍内容。
- 不把单书主题、章节聚类、概念网络塞进图书馆。

### 5.3 未来可扩展

未来书多以后，可以增加：

- 书架 / 集合。
- 用户自定义标签。
- 阅读优先级。
- 最近分析 / 最近阅读。
- 有新读后笔记的书。

这些必须来自数据库或用户显式配置。

## 6. 书籍导航页规范

书籍导航页是本系统的核心页面。它服务于“读之前看懂全书架构，读的时候定位重点，读完后回顾理解”。

### 6.1 页面职责

书籍导航页必须回答：

- 这本书的核心论题是什么？
- 哪些章节最值得读？
- 为什么读这些章节？
- 哪些章节属于同一主题？
- 哪些概念跨章节出现？
- 作者用了什么证据支撑关键观点？
- 如果我只关心某个问题，应该从哪里读？
- 读完后哪些内容值得沉淀？

### 6.2 首屏结构

首屏应该承载全局地图，而不是堆很多小统计。

```text
书名 / 作者 / 封面 / 真实标签
一句话总论
小统计卡：章节数、必读数、主题数、证据数

主画布：
主题聚类地图 + 章节热力条 + 当前主题说明
```

不需要显示：

- “已解析”这类用户看页面内容就能知道的信息。
- 虚构阅读模式，如“先地图 / 先问题 / 先证据”。
- 后台组件拼装逻辑。

### 6.3 主要模块顺序

建议顺序：

1. **全书总论**：一句话说明这本书到底在解决什么问题。
2. **主题聚类地图**：把章节按知识主题分组，而不是按原目录机械排列。
3. **章节热力条**：全书所有章节一屏可扫，显示价值分、推荐等级、是否有详情页。
4. **当前主题证据板**：展示该主题下的论证点、关键证据、推荐阅读顺序。
5. **概念网络**：概念与章节、主题、证据的关系。
6. **核心框架速览**：本书的模型、方法、判断规则。
7. **关键案例 / 研究 / 时间线**：按书的内容性质选择组件。
8. **完整章节矩阵**：所有章节的中文命名、核心命题、价值分、推荐理由、详情入口。
9. **读后理解入口**：用户后续对话、备注、永久笔记候选。

### 6.4 主题聚类

主题聚类是“按理解结构重新组织章节”，不是普通分类按钮。

每个主题至少包含：

```json
{
  "id": "trauma-body",
  "name": "创伤如何进入身体",
  "thesis": "这一组章节解释创伤不是过去事件，而是身体持续处在威胁状态。",
  "whyRead": "先读它可以理解全书为什么不把创伤当作单纯心理问题。",
  "chapters": ["ch01", "ch04", "ch05", "ch06"],
  "concepts": ["body keeps the score", "fight/flight/freeze"],
  "evidenceRefs": ["ev001", "ev014"],
  "recommendedOrder": ["ch01", "ch05", "ch06", "ch04"]
}
```

### 6.5 交互原则

任何切换都必须改变主内容区域，而不是只替换角落里一小段文字。

点击主题时：

- 主画布高亮该主题章节。
- 章节热力条过滤或强调相关章节。
- 证据板显示该主题的关键论证。
- 概念网络突出相关概念。
- 章节矩阵可自动筛选到相关章节。

点击概念时：

- 显示定义。
- 显示出现章节。
- 显示关联主题。
- 显示支撑证据和可追问入口。

点击章节时：

- 显示章节在全书中的角色。
- 显示为什么推荐或为什么跳过。
- 有详情页时进入详情页。

点击证据时：

- 展开原文出处。
- 显示 AI 转述。
- 显示可回原书精读的位置。

### 6.6 信息密度原则

- 首屏必须让用户看到全书结构，而不是只有标题和大留白。
- 同一类别的内容尽量在同一个视觉区域内完成，不让用户为少量信息长距离滚动。
- 小信息用小卡片、表格行、tooltip、抽屉或折叠面板。
- 大逻辑用大面积主画布，如主题地图、因果链、时间线、矩阵。
- 空数据不占大块空间。没有案例就不显示案例模块，没有研究就不显示研究时间线。
- 文本以“短结论 + 可展开证据”为主。

## 7. 章节详情页规范

章节详情页不是章节摘要页，而是章节论证拆解页。

### 7.1 页面职责

章节详情页必须回答：

- 本章在全书中的作用是什么？
- 本章起始问题是什么？
- 作者如何一步步推出结论？
- 哪些案例、研究或原文支撑这个推导？
- 本章和前后章节、其他主题有什么关系？
- 为什么我需要读这一章？
- 读完这一章可以沉淀什么理解？

### 7.2 顶部结构

```text
Home icon：返回图书馆页
返回书籍主页按钮
章节编号 / 英文标题 / 中文理解名
所属主题
价值分与推荐等级
本章一句话
为什么读这一章
在全书中的角色：起点 / 桥梁 / 方法 / 证据 / 结论
```

“在全书中的角色”必须来自分析，不是前端固定标签胡编。

章节页、主题页和证据页都必须能回到书籍导航页。章节页左上角固定显示一个 Home icon 直达 Library，并保留一个返回 Book Home 的文字按钮；不使用完整面包屑，避免导航占用内容空间。

### 7.3 主内容视图

章节页建议使用大面积切换视图：

1. **Overview**：本章关键点、适合谁读、读完得到什么。
2. **Argument Chain**：起始问题 → 概念解释 → 证据 → 推导 → 结论。
3. **Evidence Board**：案例、研究、原文引用、作者论断按类型分组。
4. **Concept Cards**：本章概念定义、误解、相关章节。
5. **Cases / Stories**：具体案例说明。
6. **Research Timeline**：研究、历史节点、理论变化。
7. **Methods / Decisions**：方法论、判断规则、行动建议。
8. **Source & Quotes**：短引用、出处、回原书位置。
9. **My Notes**：读后备注、AI 追问结果、永久笔记候选。

主视图可以压缩展示，但证据不能被压缩掉。任何缩略卡、案例卡、研究节点、论证链节点都应通过 `sourceRef` 打开统一的 Evidence Drawer。

Evidence Drawer 负责显示：

- 短引用或原文线索。
- 章节 / 小节 / 页码范围。
- 证据类型。
- 证据摘要。
- 为什么这条证据支撑当前结论。
- AI 对这条证据的理解。
- 用户精读时应该回到哪里。

如果当前数据没有精确页码或短引用，只显示已有的章节范围和摘要，不伪造原文。

### 7.4 论证链节点格式

```json
{
  "id": "node-01",
  "role": "起始问题",
  "claim": "作者首先把创伤从事件重新定义为身体的持续反应。",
  "authorSays": "作者观点的转述，必须有出处。",
  "aiUnderstanding": "AI 对这一节点在全章中的解释。",
  "personalValue": "只在有用户上下文或 Phase 4 时出现。",
  "evidenceRefs": ["ev001", "ev002"],
  "sourceRefs": ["ch05:120-134"],
  "relatedChapters": ["ch01", "ch06"]
}
```

### 7.5 证据类型

每条证据必须标注类型：

| 类型 | 含义 |
| --- | --- |
| `quote` | 作者原文短引用。 |
| `case` | 书中的具体人物、故事、临床案例。 |
| `research` | 研究、实验、论文、数据。 |
| `author_claim` | 作者直接论断。 |
| `method` | 作者提出的方法或实践建议。 |
| `comparison` | 对比、前后变化、反例。 |

### 7.6 AI 理解与个人价值

章节页必须区分三层：

```text
作者说了什么：来自原文和出处
AI 怎么理解：模型对上下文的解释
我为什么需要：用户读后对话或个人记忆产生的价值点
```

如果没有用户个人上下文，就不显示“对我有什么用”的强结论，只显示“可能适合追问的问题”。

## 8. 组件使用规范

初期版本优先复用现有 `book-to-webpage` 和本地 `book-analyst` 组件，不额外发明大组件。

前端组件的视觉样式、结构和交互模式应固定。AI Agent 不应该为每本书重新设计组件；AI Agent 只负责生成符合契约的 JSON / Markdown 内容。

渲染关系：

```text
固定组件模板 + 固定主题 token + AI 生成 JSON/Markdown
  → 书籍导航页
  → 章节详情页
  → 可追溯的静态读书导航
```

### 8.0 页面槽位

前端页面应按“固定槽位 + 可选组件”拼装。固定槽位保证所有书一致，可选组件根据书籍内容是否存在决定是否显示。

书籍导航页固定槽位：

```text
BookIdentity
  书名、作者、封面、真实标签、小统计卡

BookThesis
  一句话总论、这本书解决的核心问题

GlobalMap
  主题聚类地图、章节热力条、当前主题摘要

ThemeEvidence
  当前主题的论证点、证据、推荐阅读顺序

ConceptNetwork
  概念、主题、章节、证据的关系

FrameworkShelf
  核心框架、方法、判断规则

ChapterMatrix
  全章节分级表和详情入口

ReflectionDock
  读后追问、个人备注、永久笔记候选
```

章节详情页固定槽位：

```text
ChapterIdentity
  章节编号、原名、中文理解名、所属主题、价值分

ChapterRole
  本章在全书中的作用、为什么读、读完得到什么

ArgumentCanvas
  论证链主画布

EvidenceCanvas
  案例、研究、引用、作者论断

ConceptCanvas
  概念卡、误解、相关章节

MethodCanvas
  方法论、判断规则、行动建议

SourceDrawer
  原文出处、短引用/原文线索、证据摘要、AI 解读、回原书位置

PersonalReflection
  用户读后备注、AI 整理、知识库保存入口
```

可选组件只能填入这些槽位，不应改变页面职责。

### 8.1 可用组件

| 组件 | 用途 |
| --- | --- |
| `causal_chain` | 因果推进、论证链。 |
| `timeline` | 历史演进、研究时间线。 |
| `matrix` | 多维比较、章节价值矩阵。 |
| `decision_tree` | 分支判断、方法选择。 |
| `story_card` | 案例叙事。 |
| `quote_card` | 关键原文短引用。 |
| `before_after` | 前后状态对比。 |
| `type_selector` | 多类别切换。 |
| `accordion` | 分层展开、减少视觉压力。 |
| `questions` | 读前问题、读后自检、追问入口。 |
| `concept_grid` | 概念星图、概念到章节的关联。 |
| `rules` | 判断规则、行动规则、读书策略。 |

### 8.2 组件选择原则

- 内容是因果推导，用 `causal_chain`。
- 内容是时间演变，用 `timeline`。
- 内容是多维对比，用 `matrix`。
- 内容是条件判断，用 `decision_tree`。
- 内容是故事或案例，用 `story_card`。
- 内容依赖作者精确表述，用 `quote_card`。
- 内容信息多但层级清楚，用 `accordion`。
- 内容是读者行动或自检，用 `questions`。

### 8.3 禁止展示后台拼装

前端不显示：

- “本区块使用 causal_chain 组件”。
- “组件拼装谱系”。
- “AI 选择了 matrix 因为……”。

这些只存在于生成日志、JSON 或调试视图，不进入用户页面。

### 8.4 静态渲染规则

前端根据文件是否存在和数据是否为空决定展示内容：

```text
存在 analysis/book.json
  → 书籍可进入导航页。

存在 analysis/chapters/ch05.json
  → Ch05 有详情内容，可显示详情入口。

存在 analysis/themes/*.json
  → 显示主题聚类地图。

存在 analysis/evidence/*.json
  → 显示证据板和 Source Drawer。

不存在对应数据
  → 不渲染该模块，不占大块空白。
```

不允许前端为了填满页面而生成假内容。空状态只能用于明确告诉用户“尚未生成 / 可继续分析 / 可读后补充”。

## 9. 数据契约

数据契约是系统的真正接口。HTML 可以是一次性静态产物，也可以由前端运行时读取 JSON 渲染；但两者都必须遵守同一套数据语义。

V1 的可复用页面槽位、文件布局、后端元数据边界和 JSON 字段以 `docs/BOOK_ANALYST_TEMPLATE_CONTRACT.md` 为准；本章保留核心语义说明。

### 9.1 Book

```json
{
  "id": "the-body-keeps-the-score",
  "title": "The Body Keeps the Score",
  "author": "Bessel van der Kolk",
  "language": "en",
  "tags": ["trauma", "body", "therapy"],
  "thesis": "一句话总论",
  "stats": {
    "chapterCount": 20,
    "mustReadCount": 8,
    "themeCount": 5,
    "evidenceCount": 42
  },
  "paths": {
    "source": "source/the-body-keeps-the-score.epub",
    "analysis": "analysis/book.json",
    "web": "web/index.html",
    "notes": "notes/Reading Guide.md"
  }
}
```

### 9.2 Chapter

```json
{
  "id": "ch05",
  "originalTitle": "Body-Brain Connections",
  "readerTitle": "创伤如何改变身体警报系统",
  "coreClaim": "本章解释创伤如何改变身体和大脑的警觉机制。",
  "valueDensity": 5,
  "recommendation": "must-read",
  "whyRead": "它是理解全书身体论证的关键章节。",
  "roleInBook": "核心支撑",
  "themes": ["trauma-body"],
  "hasDetailPage": true,
  "sourceRange": "第5章 · 约第120-145页"
}
```

### 9.3 Evidence

```json
{
  "id": "ev001",
  "type": "research",
  "title": "脑成像研究显示创伤记忆激活身体警报系统",
  "authorSays": "对原文观点的转述。",
  "shortQuote": "合规长度内的短引用，可为空。",
  "aiUnderstanding": "AI 对证据作用的解释。",
  "sourceRefs": ["ch05:120-134"],
  "supports": ["node-01", "trauma-body"],
  "confidence": "high"
}
```

### 9.4 Personal Insight

```json
{
  "id": "pi001",
  "bookId": "the-body-keeps-the-score",
  "sourceRefs": ["ch05:120-134"],
  "relatedConcepts": ["trauma-body", "nervous-system"],
  "userNote": "用户自己的读后理解。",
  "aiSynthesis": "AI 根据对话整理出的解释。",
  "saveTo": ["obsidian", "database"],
  "createdAt": "2026-06-28"
}
```

### 9.5 Book Metadata

上传或导入书籍时生成基础元数据。它和 AI 分析数据分开保存。

```json
{
  "id": "the-body-keeps-the-score",
  "title": "The Body Keeps the Score",
  "author": "Bessel van der Kolk",
  "year": 2014,
  "language": "en",
  "sourceFormat": "epub",
  "sourcePath": "source/the-body-keeps-the-score.epub",
  "coverPath": "covers/the-body-keeps-the-score.jpg",
  "readingStatus": "to-read",
  "parseStatus": "not-parsed",
  "createdAt": "2026-06-28",
  "updatedAt": "2026-06-28"
}
```

基础元数据可以存到 SQLite、JSON 文件、GitHub 仓库、对象存储或其他后端。它不应混入 AI 对书籍内容的判断。

## 10. 生成流程规范

### 10.1 阶段一：全书拆解

- 提取全文。
- 识别章节边界。
- 建立 `INDEX.md` 或等价导航文件。
- 生成章节摘要。
- 生成术语表、模式表、cheatsheet。
- 禁止全书大文本一次性塞进上下文。

### 10.2 阶段二：上帝视角

- 一句话总论。
- 论证树。
- 水分标注。
- 关键概念速查表。
- 初步主题候选。

### 10.3 阶段三：章节分级

每章必须有：

- 原标题。
- 中文理解名。
- 核心命题。
- 价值分。
- 推荐等级。
- 推荐理由。
- 所属主题。
- 是否生成详情页。

### 10.4 阶段四：主题聚类与证据链

每个主题必须有：

- 主题论题。
- 相关章节。
- 推荐阅读顺序。
- 为什么读。
- 能得到什么。
- 核心概念。
- 支撑证据。
- 可追问问题。

### 10.5 阶段五：页面生成

生成：

- `web/index.html`：书籍导航页。
- `web/chapters/*.html`：高价值章节详情页。
- `notes/*.md`：可在 Obsidian 阅读的纯文本笔记。
- `analysis/*.json`：未来前端动态渲染的数据源。

初期仍可以输出单文件 HTML，但内容结构必须已经符合 JSON 契约。

### 10.6 阶段六：读后沉淀

读后内容只有在用户主动交流后生成。

可保存：

- 用户原话。
- AI 整理。
- 关联章节。
- 关联概念。
- 是否进入永久笔记。
- 是否进入数据库知识点。

## 11. 视觉与密度规范

### 11.1 主题 token

初期不重新发明整套视觉系统，优先使用现有主题：

- `warm-paper`
- `minimal`
- `dark`
- `ink-wash`
- `vintage-editorial`
- `paper-ink`

页面结构不随主题变化。主题只控制 token：

- 字体。
- 背景。
- 纸面/面板。
- 线条。
- 强调色。
- 阴影。
- 状态色。

### 11.2 信息密度

默认密度应该是 `balanced`：

- 比传统文章页更密。
- 比极端 dashboard 更可读。
- 让用户一屏能看到结构，但关键证据可以展开。

密度模式：

| 模式 | 适合 |
| --- | --- |
| `comfortable` | 阅读障碍友好、低压力浏览。 |
| `balanced` | 默认。结构清楚，信息量足。 |
| `dense` | 复盘、查找、章节矩阵、证据索引。 |

### 11.3 减少留白的方法

- 用一屏主画布承载全书结构。
- 用横向章节热力条代替长章节列表。
- 用矩阵和表格合并同类信息。
- 用抽屉承载出处和原文细节。
- 主卡片可以缩略，但必须把原文论据和 AI 解读放进 Evidence Drawer。
- 用 tooltip / popover 展示短定义。
- 用折叠组件承载长证据。
- 空数据模块不渲染。

## 12. Source Trace 与版权边界

### 12.1 每块内容必须有来源

凡是来自书的内容，都应有：

- 章节。
- 小节或位置。
- 约页码范围。
- 证据类型。

格式：

```text
第 X 章 第 Y 节 · 约第 N-M 页
```

### 12.2 引用策略

- 以转述为主。
- 短引用用于关键原话。
- 引用必须可追溯。
- 不输出长段原文。
- 拿不准的内容标 `[需核查]`。

## 13. 页面状态与空数据

### 13.1 未解析书籍

显示：

- 书籍元数据。
- 原文是否存在。
- 建议用户去支持 skill/workflow 的 AI Agent 触发分析。
- 可配置输出路径提醒。

不显示：

- 虚构摘要。
- 虚构章节。
- 虚构主题。

### 13.2 部分解析书籍

允许只显示已有数据：

- 有主题显示主题。
- 有章节分级显示章节矩阵。
- 没有证据链就不显示证据板。
- 没有详情页的章节只显示推荐理由，不给假链接。

### 13.3 读后未沉淀

显示读后入口和空状态，但不占大篇幅。

## 14. 质量门槛

生成完成前必须检查：

- 书籍导航页能回答“为什么读、先读哪里、读完得到什么”。
- 每个主题有相关章节和推荐顺序。
- 每个高价值章节有详情页或明确原因。
- 章节详情页有论证链，不只是摘要。
- 证据能回到原文位置。
- AI 理解和作者观点分开。
- 用户个人价值点只来自 Phase 4 或已有记忆。
- 没有虚构标签、虚构阅读模式、虚构证据。
- 没有大面积空白模块。
- 页面切换会改变主内容区域。
- HTML 可点击、无残留占位符。

## 15. V1 范围

V1 应该做到：

- 复用当前图书馆页作为本地预览和上传入口。
- 复用 book-to-webpage 组件和主题 token。
- 固定书籍导航页和章节详情页的组件样式。
- 让 AI Agent 生成符合契约的 JSON / Markdown。
- 输出书籍导航页。
- 对 value >= 4 的章节输出详情页。
- 生成可读 Markdown 笔记。
- 每个内容块有 source trace。
- 支持 Phase 4 读后对话保存到 Markdown 或 JSON。
- 允许生成结果作为纯静态页面独立打开或部署。

V1 暂不做：

- 完整语义搜索。
- 多用户权限。
- 在线协作。
- 自动长期记忆写入，除非用户确认。
- 复杂可视化图库。
- 复杂在线后端。除上传和元数据保存外，不把分析流程做进 Web 服务。

## 16. 关键原则总结

```text
图书馆页管理书。
书籍导航页理解书。
章节详情页拆论证。
Source trace 负责可信。
AI 理解负责解释。
用户读后沉淀负责个人知识。
组件服务内容，不让内容服务组件。
Skill 是业务核心，Web 是静态可视化产物。
```
