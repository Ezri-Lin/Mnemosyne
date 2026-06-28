# Mnemosyne

> **The Mother of Memory** · 你的个人阅读伴侣。
> Mnemosyne（希腊语：Μνημοσύνη）是记忆女神，九位缪斯之母。
> 展示经 AI 分析后的书籍架构页面 + 章节详情。

## 架构

```
Mnemosyne 是纯展示层。AI 分析由 Hermes Agent 在聊天中完成。

📚 上传（Mnemosyne Web 或直接放入 vault）
   ↓
🧠 *Hermes Agent 分析*（在 Hermes 聊天中，按 book-analysis skill 方法论）
   · Phase 1: God's-eye View（论题 + 论证树 + 水分标注）
   · Phase 2: 章节分级（价值密度 × 个人推荐）
   · Phase 3: 生成 HTML（索引页 + 章节详情页）
   · Phase 4: 对话深读（可选）
   ↓
🖼️ Mnemosyne 展示（书架 + 架构页 + 章节详情页）
   ↓
📝 笔记同步至 Obsidian vault（Golden-House）
```

## 核心方法论：`skill/book-analysis/`

```
skill/book-analysis/
├── SKILL.md                        ← 完整工作流（Hermes 可加载）
├── references/
│   ├── the-body-keeps-the-score-reference.md  ← 标杆产出参考
│   └── html-patterns.md            ← 14 个 HTML 输出范式
└── templates/
    ├── base.html                   ← 页面骨架（暖纸主题）
    ├── components.md               ← 12 个交互组件
    └── themes/
        └── warm-paper.css          ← 默认主题 CSS
```

使用方式：
1. 确保 `book-to-webpage` skill 已安装至 `~/.hermes/skills/`
2. 在 Hermes Agent 聊天中：
   ```
   分析《书名》，加载 book-analysis skill
   ```
3. Agent 会自动读完文本、按 4-Phase 方法论分析、生成 HTML + vault 笔记

## 技术栈

- **后端**: Flask + SQLAlchemy + SQLite
- **前端**: 纯 HTML/CSS/JS（暖纸主题）
- **展示**: Poster Wall + Architecture 页 + Chapter 详情页
- **部署**: Docker（单容器）

## 快速启动

```bash
cp .env.example .env   # 配置 vault 路径
docker compose up -d   # 启动
```

访问 http://localhost:5052 查看书架。

## 短命令

| 操作 | 命令 |
|------|------|
| 启动 | `docker compose up -d` |
| 停止 | `docker compose down` |
| 日志 | `docker compose logs -f` |
| 重建 | `docker compose up -d --build` |
| 上传 | 书架页 → 右上角上传按钮 |
| 分析 | Hermes 聊天: `分析《书名》` |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MNEMO_PORT` | 端口 | `5000`（映射 5052） |
| `MNEMO_LANG` | 默认语言 | `zh` |
| `DATABASE_URL` | 数据库连接 | `sqlite:////app/data/mnemosyne.db` |
| `VAULT_DIR` | Obsidian vault 路径 | `/app/vault` |
