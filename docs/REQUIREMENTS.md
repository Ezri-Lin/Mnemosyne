# 书籍分析系统——真需求拆解

> 基于 `skill/book-analyst` 方法论，
> 以支持 skill/workflow 的 AI Agent 为分析引擎、Mnemosyne 为展示层、
> Golden House Obsidian vault 为知识持久化层。

## 一、核心架构（3 层）

### 1. 展示层：Mnemosyne

**职责**：只做两件事——存书 + 展示。不做任何 AI 分析。

| 功能 | 说明 | 状态 |
|------|------|------|
| 上传书籍 | 支持 EPUB/PDF/TXT → 存到 vault/source/ | ✅ 已有 |
| 书架（Poster Wall） | 封面墙，按 status/lang/rating 筛选 | ✅ 已有 |
| 书籍架构页 | 读取 vault/web/index.html 渲染 | ✅ 已有 |
| 章节详情页 | 读取 vault/web/chapters/*.html 渲染 | ✅ 已有 |
| 健康检查 | `/health` 返回服务状态 | ✅ 已有 |
| 未解析提示 | 无 web/ 时显示"请使用 book-analyst skill 分析" | ✅ 已有 |

**不需要的功能（已删除）**：
- ❌ 不触发 AI 分析
- ❌ 不调用任何 API
- ❌ 不解析/分割/提取文本
- ❌ 不生成 HTML

### 2. 分析引擎：AI Agent

**职责**：在支持 skill/workflow 的用户聊天会话中分析书籍，按 book-analyst skill 方法论执行。

**启动条件**（用户说以下任意一句）：
- `分析《书名》`
- `帮我看《书名》这本书`
- `按 The Body Keeps the Score 模板分析《书名》`

**分析流程**：见第二章《4-Phase 方法论》。

### 3. 知识持久化层：Golden House Vault

**职责**：存放分析产出，两地同步（iCloud + Git）。

**产出写回路径**：

```
Golden-House/5.0 Books & Reading/Books/<书名>/
├── 书名.md                      ← frontmatter + 核心元数据
├── Phase 1 - God's-eye View.md  ← 论题 + 论证树 + 概念速查
├── Phase 2 - Chapter Value Grading.md ← 章节分级表
├── Phase 4 - ... .md            ← 对话深读笔记（可选）
├── source/原文.txt              ← 原始文本
└── web/
    ├── index.html               ← 架构导航页
    └── chapters/
        ├── ch01-<slug>.html     ← 高价值章节详情
        ├── ch04-<slug>.html
        └── ...
```

**备注**：`Phase 3` 不存在独立文件——Phase 3 的产出就是 `web/` 目录里的 HTML。

---

## 二、4-Phase 方法论（详细）

### Phase 1: God's-eye View（全部章节）

**目标**：用一个"上帝视角"看清全书骨架。

**必须产出**：
1. **一句话 Thesis**（≤2 句）—— 这本书到底在说什么
2. **论证树** —— 核心论点 → 分论点 → 证据类型（数据/案例/逸事/纯断言）
3. **水分标注** —— 标记哪些内容可跳过（重复/注水/常识）
4. **关键概念速查表** —— 本书独有的术语/概念一览

**输出文件**：`Phase 1 - God's-eye View.md`

**质量要求**：
- 论证树必须标注证据类型（不要所有论点混在一起）
- 水分标注具体到段或页，不笼统
- 概念速查表不多于 10 个核心概念

### Phase 2: 章节分级（全部章节）

**目标**：给每一章打分，让你知道时间花在哪。

**必须产出**：

| 编号 | 英文原名 | 中文命名 | 核心命题 | 值 | 推荐 | 理由 |
|------|---------|---------|---------|---|------|-----|
| Ch 1 | ... | ... | 一句话 | 1-5 | must/skim/skip | 为什么 |

**评分规则**：
- 价值分 1-5：5=全书的"命脉"、3=有价值但非核心、1=注水/无意义
- 推荐等级：must-read（必须读）、worth-reading（值得读）、skim（略读）、skip（可跳过）
- 中文命名是**你对本章的个人理解**，不是直译英文标题
- 推荐理由写具体——"本章是全书论点的核心支撑"比"本章很有价值"有用得多

**输出文件**：`Phase 2 - Chapter Value Grading.md`

**可附加**：
- 价值分分布图（如果用户需要）

### Phase 3: 生成 HTML（只对 must-read / worth-reading 章节）

**目标**：把 AI 分析结果渲染成可浏览的 HTML 页面。

**索引页 `web/index.html`**：

| 区块 | 描述 | 来源 |
|------|------|------|
| Hero + 一句话总论 | 书名 + thesis | Phase 1 |
| 目录导航条 | 锚点链接到各分区 | 固定 |
| 必读聚类 | 按主题聚类 must-read 章节 | Phase 2 |
| 全本热力图 | 颜色编码的章节价值分布 | Phase 2 |
| 概念星图 | 跨章概念关联网络 | Phase 1 概念表 |
| 核心框架速览 | 本书核心模型/框架 | Phase 1+2 |
| 完整分级表 | Phase 2 表格，可链接到详情页 | Phase 2 |

**技术规范**：
- 继承 base.html 骨架 + warm-paper 主题
- 每个内容块加 `data-source` 属性（关联原文）
- 加深追按钮 `.deep-dive-btn`（hover 可见）
- 内部链接使用相对路径（`./chapters/ch01-<slug>.html`）
- 单文件 HTML

**章节详情页 `web/chapters/chNN-<slug>.html`**：

只对 value >= 4 的章节生成。5 标签页布局：

| 标签页 | 内容 | 组件 |
|--------|------|------|
| Overview | 关键点卡片网格 | `note`/`grid` 组件 |
| Causal Chain | 交互式因果链 | `causal_chain` 组件 |
| Frameworks | 可折叠框架 | `accordion` 组件 |
| Cases | 案例叙事卡 | `story_card` 组件 |
| Research + Decisions | 时间线 + 决策规则 | `timeline` + `rules` 组件 |

**可附加组件（按需放入索引页）**：

| 组件 | 适合场景 |
|------|---------|
| `timeline` | 书有历史演进脉络 |
| `matrix` | 有概念/方法对比 |
| `decision_tree` | 有分支判断框架 |
| `before_after` | 有前后状态对比 |
| `quote_card` | 关键原文需视觉突出 |
| `questions` | 读者自检清单 |

### Phase 4: 对话深读（可选，用户触发）

**目标**：针对用户感兴趣的内容深入讨论。

**可讨论的内容**：
- Steel-man 反方论点
- 反例/反直觉
- 与用户个人情境的关联
- 可入库的金句/笔记

**硬约束**：
- **不编造原文**：拿不准的标 `[需核查]`
- **不替用户写 permanent note**：只产出讨论笔记
- Phase 4 的内容才可以包含"与你人生的关联"
- Phase 1-3 不能编造个人化内容

---

## 三、输出规格

### 索引页必须包含的元素

1. 书名（主标题）
2. 作者 + 出版信息
3. 一句话 Thesis
4. 章节导航（至少包含 must-read 章节）
5. 热力图（颜色编码的章节价值分布）
6. 必读聚类（2-5 个主题组）
7. 概念星图或概念表
8. 完整分级表（所有章节）
9. Phase 4 入口（留白，待补充）

### 章节详情页必须包含的元素

1. 章节编号 + 英文名 + 中文名
2. 5 个标签页（Overview / Causal Chain / Frameworks / Cases / Research+Decisions）
3. Source drawer（原文出处面板）
4. 上一章/下一章导航
5. 返回索引页链接
6. 深追按钮（每个面板底部）

### Vault 笔记必须包含的元素

**书名.md**：
```yaml
---
status: <completed/reading/to-read>
priority: <P0/P1/P2/P3>
topic: <核心主题>
language: <zh/en>
author: <作者名>
year: <出版年份>
pages: <页码>
rating: <个人评分>
related: <相关书/链接>
---

Thesis: 一句话论题

已生成分析：
- [[Phase 1 - God's-eye View]]
- [[Phase 2 - Chapter Value Grading]]
- 架构页：[[web/index.html]]
```

**Phase 文件**：markdown 格式，信息密度优先

---

## 四、质量要求

### 通用约束

| 规则 | 说明 |
|------|------|
| 不编造原文 | 拿不准的标 `[需核查]`，全句 |
| 信息密度优先 | 能用表格不用段落，能用列表不用句子 |
| 双语 | 保留英文原名，中文命名是你的理解不是直译 |
| Source 追溯 | 每段分析标注对应原文范围（章节级别） |
| 零广告 | 输出中不含"这是一个分析"/"以上是"...的 AI 废话 |

### 分级质量

| 等级 | 定义 | 示例 |
|------|------|------|
| 5 | 全书核心命脉 | Ch 1 《白莲花》的 thesis 框架 |
| 4 | 核心支撑 | Ch 4 的"逃避"→"创伤"因果链 |
| 3 | 有价值扩展 | Ch 7 的补充案例 |
| 2 | 可略读 | 重复的观点或常识性铺垫 |
| 1 | 可跳过 | 注水、离题、冗余故事 |

### HTML 质量

| 检查项 | 要求 |
|--------|------|
| 自包含 | 单文件 HTML，不需外部资源 |
| 响应式 | 手机和桌面都可读 |
| 无样式断裂 | 所有组件用了主题 CSS 变量 |
| 可导航 | 索引页 ↔ 详情页的双向链路 |
| 不垮 | 超过 5000 行的文本需要分段加载 |

---

## 五、非功能性需求

| 需求 | 说明 |
|------|------|
| 每次分析需加载 `book-to-webpage` skill | 获取 base.html, components.md, themes |
| 必须有上下文 | 不在无上下文的情况下分析 |
| 不跨书共享上下文 | 每本书独立分析 |
| 输出按 vault 规范写入 | 避免污染 vault 结构 |
| Mnemosyne 不依赖分析组件 | 即使没有分析产出，展示层也能独立运行 |

---

## 六、边界与异常

| 场景 | 处理方式 |
|------|---------|
| 没有 source 文件 | 提示"未找到原文，请先上传 EPUB/TXT" |
| 只有部分章节可读 | 能读多少分析多少，标注缺失 |
| 章节结构不规则 | Agent 自行判断边界，在 Phase 1 中说明分章逻辑 |
| 用户不认可分级 | 接受 override，Phase 2 表格标注为用户自定义 |
| 原文超过模型 context | 按章节逐章喂入，标注"本章分析基于部分原文" |
| 分析中途中断 | 已产出的 HTML 和 vault 笔记保留，标注"未完成" |
| 多本书同时分析 | 建议用户逐本处理（不以 batch 模式分析） |

---

> 本文档对应 `skill/book-analyst/SKILL.md`，是方法论的项目内说明书。
> 所有对方法论本身的需求变更必须同步更新本文档和 skill。
