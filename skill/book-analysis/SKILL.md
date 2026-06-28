---
name: book-analysis
description: "Book analysis using Hermes Agent — read source text, apply 4-phase methodology, generate HTML + vault notes following The Body Keeps the Score template style. Integrates book-to-webpage component library and theme system."
---

# 书籍分析工作流（v2 — Hermes Agent 版）

## 触发条件

用户说以下任何一条：
- "分析《书名》"
- "帮我看这本书"
- "按 The Body Keeps the Score 模板分析《书名》"

## 前置准备

1. **加载 `book-to-webpage` skill** — 获取组件库、主题系统、base.html
2. **读取 `components.md`** — 了解可用组件及其适用场景（causal_chain, matrix, timeline, story_card, accordion, decision_tree, quote_card, questions, before_after, type_selector, concept_grid, rules 等）
3. **读取主题目录** — 了解 6 套主题（warm-paper, ink-wash, paper-ink, dark, minimal, vintage-editorial），默认用 warm-paper
4. **找到 source 文件** — 在 vault `5.0 Books & Reading/Books/<书名>/source/` 下

## Phase 1: God's-eye View

产出 vault 笔记 `Phase 1 - God's-eye View.md`：

- **Thesis** — 一句话核心论题
- **论证树** — 核心论点 → 分论点 → 论据的层级结构
- **水分标注** — 标记哪些章节可以跳读（skip）、可略读（skim）、必须读（must-read）
- **关键概念速查表** — 本书独有的术语/概念一览

## Phase 2: 章节分级

产出 vault 笔记 `Phase 2 - Chapter Value Grading.md`：

**章节分级表**（每行一章）：

| 编号 | 英文原名 | 中文命名 | 核心命题 | 价值分 | 推荐等级 | 推荐理由 |
|------|----------|---------|---------|-------|---------|--------|
| Ch 1 | Title | 你的命名 | 一句话 | 1-5 | must/skip | 为什么这个等级 |

- 中文命名反映你个人对本章内容的理解（不是直译英文标题）
- 推荐理由写具体：这是该章最核心的启发（不是泛泛而谈）
- 标出哪些章节可做深读

## Phase 3: 生成 HTML

核心产出。参考 `book-to-webpage` 的 `base.html` + `components.md` 选择组件。

### 索引页（`web/index.html`）

按 **The Body Keeps the Score/web/index.html** 为模板风格：

**布局结构：**
1. **Hero + 一句话总论** — thesis + 副标题
2. **目录导航条** — 锚点链接到各分区
3. **你的必读聚类** — 按主题聚类章节（参考 The Body Keeps the Score 的 5 个聚类），每类说明为什么重要
4. **全本热力图** — 以 chapter/value_density 为数据，颜色编码：红色=必读、金色=值得读、灰色=可跳过
5. **概念星图** — 跨章概念间的关联网络（选 `concept-grid` 组件）
6. **核心框架速览** — 本书的核心模型/框架（选 `note`/`grid` 组件）
7. **Phase 2 完整分级表** — 全量表格，可链接到章节详情页
8. **附加组件（按需挑选）**：
   - `timeline` — 如果书有历史演进脉络
   - `matrix` — 如果有概念/方法对比
   - `decision_tree` — 如果有分支判断框架
   - `before_after` — 如果有前后状态对比
   - `quote_card` — 关键原文引用视觉突出
   - `questions` — 读者自检清单

**技术规范：**
- 继承 base.html 骨架
- 应用 warm-paper 主题（通过 `<link>` 或内联主题 CSS）
- 每个内容块加 `data-source` 属性关联原文
- 加深追按钮（`deep-dive-btn`）在每个内容块中
- 组件 CSS/JS 通过 `{{component_styles}}` / `{{component_scripts}}` 插槽注入
- 单文件 HTML

### 章节详情页（`web/chapters/ch<num>-<slug>.html`）

只对 value_density >= 4 的章节生成。5 个标签页布局：

1. **Overview** — 关键点卡片网格（`note`/`grid` 组件）
2. **Causal Chain** — 因果链探索器（`causal_chain` 组件）
3. **Frameworks** — 框架折叠（`accordion` 组件）
4. **Cases** — 案例叙事卡（`story_card` 组件），标注出处
5. **Research + Decisions** — 时间线（`timeline` 组件）+ 决策规则速览（`rules` 组件）

每个标签页底部加 `deep-dive-btn`。

### 写入路径

```
vault/5.0 Books & Reading/Books/<书名>/
├── web/index.html
├── web/chapters/ch*.html
├── Phase 1 - God's-eye View.md
├── Phase 2 - Chapter Value Grading.md
└── source/原文.txt
```

## Phase 4: 对话深读（可选）

用户读完后可能追问，这时按需深入讨论：
- Steel-man 反方论点
- 反例/反直觉
- 与用户个人情境的关联
- 可入库的金句/笔记

**注意**：Phase 4 的内容才包含"与你人生的关联"。Phase 1-3 不编造个人化内容。

## 核心约束

- **不编造原文**：拿不准的标 `[需核查]`
- **不替用户写 permanent note**：只产出分析框架
- **信息密度优先**：能用表格不用段落，能用列表不用句子
- **双语**：保留英文原名 + 你的中文命名
- **Source 追溯**：每段分析标注对应原文范围
