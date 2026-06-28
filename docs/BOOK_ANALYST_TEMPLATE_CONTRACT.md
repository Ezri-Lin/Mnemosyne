# Book Analyst Template Contract

这份文档固定 V1 的页面模板、数据文件和后端元数据边界。目标是让 AI Agent 只生成结构化内容，前端模板负责一致地展示。

## 0. Skill 安装产物

`book-analyst` skill 必须自带可安装的空模板和空数据骨架。首次初始化项目时，执行：

```bash
python skill/book-analyst/scripts/init_project.py --project-root .
```

初始化后项目下必须出现：

```text
.book-analyst/
  config.json
  page-templates/
    library-empty.html
    book-home-empty.html
    chapter-page-empty.html
  data-skeletons/
    manifest.empty.json
    analysis/book.empty.json
    analysis/themes.empty.json
    analysis/concepts/index.empty.json
    analysis/chapters/index.empty.json
    analysis/chapters/chapter.empty.json
    analysis/evidence/index.empty.json
```

AI Agent 后续只补数据和渲染，不重新设计页面结构。

## 1. 三层页面

### 1.1 Library

用途：管理很多书，不解释单本书。

固定能力：

- 海报墙 / 列表视图。
- 上传书籍。
- 搜索。
- 阅读状态筛选。
- 解析状态筛选。
- 语言筛选。
- 排序。
- 点击进入 Book Home。

导航规则：

- Library 是根页面。
- Book Home 左上角保留返回 Library 的入口。
- Chapter Page 左上角显示 Home icon 直达 Library，并保留 Back to Book Home。
- 不使用完整面包屑，避免导航挤占阅读空间。

### 1.2 Book Home

用途：一本书的上帝视角导航页。

固定槽位：

- `BookIdentity`：书名、作者、封面、真实标签、小统计卡。
- `BookThesis`：一句话总论、核心问题、阅读前定位。
- `ThemeMap`：主题分类、主题一句话、推荐阅读顺序、读完获得什么。
- `ChapterHeatmap`：章节价值、所属主题、详情入口。
- `ThemeEvidence`：当前主题的关键论证、证据和章节连接。
- `ConceptNetwork`：概念与主题、章节、证据的关系。V1 可用列表/小卡片，不强制画复杂图。
- `FrameworkShelf`：核心框架、判断规则、方法论。
- `ReflectionDock`：读后追问、个人备注、永久笔记候选。

### 1.3 Chapter Page

用途：高价值章节的论证拆解页。

固定槽位：

- `ChapterTopNav`：Home icon 回 Library，Back button 回 Book Home。
- `ChapterIdentity`：章节编号、原名、中文理解名、所属主题。
- `ChapterRole`：本章在全书中的角色、为什么读、读完得到什么。
- `OverviewCanvas`：关键论点缩略卡。
- `ArgumentCanvas`：起始问题 -> 概念解释 -> 证据 -> 推导 -> 结论。
- `FrameworkCanvas`：本章框架、何时用、怎么用。
- `CaseCanvas`：案例卡，主区放摘要，证据抽屉放原文线索。
- `ResearchCanvas`：研究时间线、数据、作者论断。
- `MethodCanvas`：判断规则、行动建议、可带走结论。
- `EvidenceDrawer`：短引用/原文线索、位置、证据摘要、AI 解读、精读定位。

## 2. 文件布局

每本书独立保存，HTML 可静态打开，JSON/Markdown 是内容源。

```text
<Book>/
  manifest.json
  source/
    original.epub
    extracted.txt
    cover.jpg
  analysis/
    book.json
    themes.json
    concepts.json
    chapters/
      index.json
      ch10-developmental-trauma.json
    evidence/
      index.json
  notes/
    reading-guide.md
    personal-reflections.md
    permanent-note-candidates.md
  web/
    index.html
    chapters/
      ch10-developmental-trauma.html
```

V1 可以只生成 `web/*.html`，但 HTML 内的数据结构必须能回推到这些 JSON 字段。

## 3. 后端元数据边界

Mnemosyne 后端只保存书籍元数据和上传状态，不保存完整分析内容。

现有 `books` 表可作为 V1 metadataStore：

```json
{
  "slug": "the-body-keeps-the-score",
  "title": "The Body Keeps the Score",
  "author": "Bessel van der Kolk",
  "lang": "en",
  "status": "reading",
  "rating": 0,
  "year": 2014,
  "tags": ["trauma", "psychology"],
  "source_format": "epub",
  "source_path": "source/original.epub",
  "vault_path": "Books/The Body Keeps the Score",
  "notes": "",
  "last_analyzed": "2026-06-29T12:00:00"
}
```

解析状态规则：

- `parsed`：存在 `web/index.html` 或 `last_analyzed` 有值。
- `not-parsed`：只有元数据和 source，没有分析产物。
- `queued`：用户上传后等待 AI Agent 处理。

后端 API V1：

| API | 职责 |
| --- | --- |
| `GET /api/books` | 返回 Library 所需书籍列表。 |
| `POST /api/upload` | 保存 source，提取封面/标题/作者等基础信息。 |
| `PUT /api/status/<slug>` | 更新阅读状态。 |
| `GET /book/<slug>/` | 返回该书 `web/index.html`，不存在则返回未解析页。 |
| `GET /book/<slug>/<path>` | 返回章节 HTML、图片、静态资源。 |

不把主题、证据、章节分析写进 SQL 表；这些内容由 AI Agent 写入 `analysis/` 和 `web/`。

## 4. JSON 数据契约

### 4.1 manifest.json

```json
{
  "schemaVersion": "book-analyst-v1",
  "bookId": "the-body-keeps-the-score",
  "generatedAt": "2026-06-29T12:00:00",
  "language": "zh-CN",
  "theme": "warm-paper",
  "sourcePolicy": "short-with-source",
  "paths": {
    "bookHome": "web/index.html",
    "analysis": "analysis/book.json",
    "chapters": "analysis/chapters",
    "evidence": "analysis/evidence/index.json"
  }
}
```

### 4.2 analysis/book.json

```json
{
  "id": "the-body-keeps-the-score",
  "title": "The Body Keeps the Score",
  "author": "Bessel van der Kolk",
  "year": 2014,
  "language": "en",
  "cover": "source/cover.jpg",
  "tags": ["trauma", "body", "therapy"],
  "thesis": "一句话总论。",
  "coreQuestion": "这本书试图解决什么问题？",
  "readingRoute": "推荐阅读路线。",
  "stats": {
    "chapterCount": 22,
    "mustReadCount": 8,
    "themeCount": 5,
    "evidenceCount": 42
  }
}
```

### 4.3 analysis/themes.json

```json
{
  "themes": [
    {
      "id": "developmental-trauma",
      "title": "发育创伤",
      "oneLine": "这个主题解释早期关系如何塑造身体和大脑。",
      "whyRead": "为什么用户应该先读这个主题。",
      "readingOrder": ["ch10", "ch11", "ch12"],
      "whatYouGet": "读完获得的理解。",
      "chapterIds": ["ch10", "ch11"],
      "conceptIds": ["dtd", "epigenetics"],
      "evidenceIds": ["ev-meaney", "ev-minnesota"]
    }
  ]
}
```

### 4.4 analysis/chapters/index.json

```json
{
  "chapters": [
    {
      "id": "ch10",
      "number": 10,
      "originalTitle": "Developmental Trauma: The Hidden Epidemic",
      "readerTitle": "发育创伤：看不见的伤害",
      "roleInBook": "bridge",
      "valueDensity": 5,
      "recommendation": "must-read",
      "themeIds": ["developmental-trauma"],
      "detailPage": "web/chapters/ch10-developmental-trauma.html",
      "sourceRange": "Chapter 10"
    }
  ]
}
```

### 4.5 analysis/chapters/chXX.json

```json
{
  "id": "ch10",
  "chapterNumber": 10,
  "originalTitle": "Developmental Trauma: The Hidden Epidemic",
  "readerTitle": "发育创伤：看不见的伤害",
  "oneLine": "本章把早期关系、身体调节和诊断失败连成一条线。",
  "whyRead": "它是理解复杂创伤儿童为什么会被误诊的关键章节。",
  "whatYouGet": "读完得到一个发育创伤框架。",
  "roleCards": [
    {"label": "Chapter Role", "value": "核心桥梁", "body": "从创伤反应进入发育中的大脑如何被关系塑形。"}
  ],
  "overviewCards": [
    {
      "id": "ov-genes",
      "role": "起点",
      "title": "Genes Are Not Destiny",
      "body": "作者先拆掉坏基因解释一切的路径。",
      "use": "不要把长期反应简化成先天缺陷。",
      "sourceRef": "ev-bad-genes"
    }
  ],
  "argumentChain": [
    {
      "id": "node-care",
      "role": "诱因",
      "claim": "不可预测照护让身体始终戒备。",
      "logic": "一致照护让孩子学会自我调节；不可预测照护重置压力基线。",
      "next": "node-arousal",
      "evidenceRefs": ["ev-minnesota"]
    }
  ],
  "frameworks": [],
  "cases": [],
  "research": [],
  "decisionRules": []
}
```

### 4.6 analysis/evidence/index.json

```json
{
  "evidence": [
    {
      "id": "ev-minnesota",
      "type": "research",
      "title": "Minnesota Longitudinal Study",
      "sourceRange": "Chapter 10 · Minnesota study",
      "shortQuote": "",
      "sourceHint": "原文线索：长期追踪中，亲子关系质量比 IQ、气质等变量更有解释力。",
      "summary": "180 名儿童长期追踪显示，亲子关系质量是行为结果的重要预测因素。",
      "whyImportant": "支撑关系质量比单一个体特质更关键。",
      "aiUnderstanding": "这条证据让本章从个体缺陷视角转向关系系统视角。",
      "readLocation": "精读时关注研究变量比较，而不只是结论。",
      "supports": ["node-care", "developmental-trauma"]
    }
  ]
}
```

## 5. AI 生成边界

AI Agent 可以生成：

- JSON 字段内容。
- Markdown 笔记。
- 页面内文本。
- 组件所需列表、节点、证据关系。

AI Agent 不应该生成：

- 新页面结构。
- 新视觉系统。
- 没有来源的标签、分类、阅读模式。
- 不存在的引用或证据。
- 大段原文复制。

空数据规则：

- 没有 `cases` 就不渲染 CaseCanvas。
- 没有 `research` 就不渲染 ResearchCanvas。
- 没有 `sourceRef` 的书籍内容不能进入正式页面。
- 个人化内容只进入 `PersonalReflection`，除非用户明确开启。

## 6. 前端渲染规则

固定模板读取固定数据：

```text
Library template
  <- metadataStore / GET /api/books

Book Home template
  <- analysis/book.json
  <- analysis/themes.json
  <- analysis/chapters/index.json
  <- analysis/evidence/index.json

Chapter template
  <- analysis/chapters/chXX.json
  <- analysis/evidence/index.json
```

交互状态只影响展示，不改变数据语义：

- `selectedThemeId`
- `selectedChapterId`
- `selectedSourceRef`
- `activeTab`
- `density`
- `theme`

所有 source chip 都打开同一个 `EvidenceDrawer`。主卡片负责快速导航，抽屉负责保存论据、原文线索和 AI 理解。

## 7. V1 验收标准

- Library 能管理多本书，书多时仍可搜索、筛选、排序。
- Book Home 能按主题切换，并让右侧内容跟随主题变化。
- Chapter Page 主区信息密度高，source 抽屉保留证据层。
- 页面没有虚构标签、虚构模式、虚构证据。
- 所有书都使用同一套模板和主题 token。
- 缺数据的模块不显示，不留下大块空白。
- 生成结果可静态打开，也可由 Flask 读取展示。
