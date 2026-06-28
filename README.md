<p align="center">
  <img src="static/brand/mnemosyne-logo.svg" alt="Mnemosyne Codex Seal" width="84">
</p>

# Mnemosyne

> AI Book Analyst for visual reading maps, chapter guides, and reusable knowledge skills.

Mnemosyne is the product and display layer. It stores books, shows a Library, and serves the generated Book Home and Chapter Page artifacts.

The installable workflow is the **`book-analyst` skill**. It is intentionally agent-agnostic: Codex, Claude Code, Hermes, OpenClaw, WorkBuddy, or any AI assistant that can load skills/workflows can use the same methodology.

## What This Is

Mnemosyne is not a normal summary app. The goal is to let an AI Agent read like a teacher preparing a lesson:

1. split the book into manageable chapters
2. identify high-value chapters instead of reading everything into one context
3. build themes, concepts, evidence chains, quotes, and reading routes
4. render a visual navigation system before the user starts deep reading
5. keep Markdown/JSON outputs usable for Obsidian, Git, static hosting, or future knowledge skills

The result is a three-layer reading artifact:

```text
Library
  Many books, upload/status/search/sort/filter.

Book Home
  One book's god's-eye map: thesis, themes, chapter heatmap, concept network,
  evidence links, frameworks, and recommended reading route.

Chapter Page
  One important chapter's detailed guide: role, argument chain, frameworks,
  cases, research, decisions, source evidence, and AI understanding.
```

## Repository Layout

```text
skill/book-analyst/
  SKILL.md                         # workflow entry for AI Agents
  agents/openai.yaml               # optional agent metadata
  assets/page-templates/           # empty Library / Book Home / Chapter shells
  assets/data-skeletons/           # JSON skeletons for analysis output
  references/                      # workflow, schema, template contract
  scripts/                         # init, extract, split, render, serve, validate
  templates/                       # existing HTML component references

docs/
  BOOK_ANALYST_SYSTEM_SPEC.md      # business rules and page responsibilities
  BOOK_ANALYST_TEMPLATE_CONTRACT.md# template/data/backend contract

web/
  Existing generated or hand-tested HTML artifacts
```

## Quick Install

From a local checkout:

```bash
./scripts/install-book-analyst
```

Or install directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/Ezri-Lin/Mnemosyne/main/scripts/install-book-analyst | bash
```

The installer copies the complete `skill/book-analyst/` package into the local skill directory, including scripts, page templates, references, and JSON skeletons.

Default install target:

```text
${CODEX_HOME:-$HOME/.codex}/skills/book-analyst
```

For other agents, pass that agent's skill directory:

```bash
./scripts/install-book-analyst --skills-dir /path/to/agent/skills
```

After installing, restart the AI Agent and say:

```text
Use $book-analyst to configure my book library, analyze this book,
and generate the Library, Book Home, and Chapter Page outputs.
```

The installer prints this activation prompt after a successful install.

## Manual Install

If you prefer to copy files yourself:

```bash
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/book-analyst
cp -R skill/book-analyst ~/.codex/skills/book-analyst
```

Then restart the AI Agent and invoke `book-analyst`.

Example prompt:

```text
Use the book-analyst skill to configure my book library, analyze this book,
and generate the Library, Book Home, and Chapter Page outputs.
```

## Analyze A Book

Initialize a project:

```bash
python skill/book-analyst/scripts/init_project.py --project-root .
```

Prepare one source book:

```bash
python skill/book-analyst/scripts/run_flow.py --project-root . --source path/to/book.epub
```

The deterministic scripts copy the source, extract text when possible, split chapters, install empty templates, and create the expected project layout. The AI Agent then fills the structured files under `analysis/<book-id>/`.

Render the fixed front-end templates:

```bash
python skill/book-analyst/scripts/render_project.py --config .book-analyst/config.json --book-id <book-id>
```

Serve generated HTML:

```bash
python skill/book-analyst/scripts/start_service.py --config .book-analyst/config.json --port 8765
```

After rerendering, refresh the browser. The static service does not need to restart.

## Server Setup: Hermes + Obsidian Vault

Use this path when the server uses Hermes as the AI Agent and an Obsidian vault as the durable book database.

Clone and enter the repo:

```bash
git clone https://github.com/Ezri-Lin/Mnemosyne.git
cd Mnemosyne
```

Install the skill into Hermes. Change the path if your Hermes skill folder is different:

```bash
./scripts/install-book-analyst --skills-dir "${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
```

Configure the Obsidian vault path:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
VAULT_DIR=/home/lighthouse/Golden-House
MNEMO_PORT_EXTERNAL=5052
```

Start Mnemosyne:

```bash
docker compose up -d --build
```

Open:

```text
http://<server-ip>:5052
```

Then restart Hermes and say:

```text
Use $book-analyst to configure my book library.
My Obsidian vault is /home/lighthouse/Golden-House.
Save book sources, analysis JSON, notes, and generated web pages under the vault.
```

Typical book output location:

```text
<Obsidian Vault>/5.0 Books & Reading/Books/<Book Title>/
  source/
  analysis/
  notes/
  web/index.html
  web/chapters/*.html
```

Mnemosyne reads this vault output and serves the Library, Book Home, and Chapter Page HTML. Hermes does the analysis; Mnemosyne does storage, upload metadata, and display.

## Generate A Knowledge Skill

After a book has meaningful structured analysis, it can become a reusable thinking aid:

```bash
python skill/book-analyst/scripts/generate_book_skill.py analysis/<book-id> --output-root generated-skills
```

This produces a small `<book-id>-knowledge` skill from the book's thesis, concepts, and reasoning lenses.

## Mnemosyne App

The Flask app is the optional local display layer:

- stores uploaded books and metadata
- shows the poster-wall Library
- tracks reading and parse status
- serves `web/index.html` and `web/chapters/*.html`
- does not call an LLM or perform the book analysis itself

Quick start:

```bash
cp .env.example .env
docker compose up -d
```

Open http://localhost:5052 to view the Library.

Useful commands:

| Action | Command |
| --- | --- |
| Start app | `docker compose up -d` |
| Stop app | `docker compose down` |
| Logs | `docker compose logs -f` |
| Rebuild | `docker compose up -d --build` |
| Validate skill project | `python skill/book-analyst/scripts/validate_project.py --config .book-analyst/config.json` |

## Environment

| Variable | Purpose | Default |
| --- | --- | --- |
| `MNEMO_PORT` | Flask app port | `5000` mapped to `5052` |
| `MNEMO_LANG` | Default UI language | `zh` |
| `DATABASE_URL` | Metadata database | `sqlite:////app/data/mnemosyne.db` |
| `VAULT_DIR` | Book vault path | `/app/vault` |
