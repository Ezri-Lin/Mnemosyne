# Workflow

Use this file when generating or updating a full book analysis.

## 1. Configure

If `.book-analyst/config.json` is missing, run:

```bash
python skill/book-analyst/scripts/init_project.py --project-root .
```

The config defines where source books, analysis JSON, static HTML, notes, knowledge outputs, and metadata live.

## 2. Import Book

Book upload/import only creates metadata and saves source files. It does not perform AI analysis.

Minimum metadata:

- slug
- title
- author
- year
- language
- reading status
- source format
- source path
- cover path when available

Use:

```bash
python skill/book-analyst/scripts/prepare_book.py path/to/book.epub --config .book-analyst/config.json
```

This command copies the original file, extracts `extracted.txt`, writes `metadata.json`, splits chapters, and creates empty per-book analysis files.

For an interactive one-shot start:

```bash
python skill/book-analyst/scripts/run_flow.py --project-root . --source path/to/book.epub
```

## 3. Extract and Index

Extract full text and metadata. Build a chapter boundary index first.

Do not load a large book into one context. Use chapter boundaries and targeted slices.

## 4. First-Pass Analysis

Generate:

- one-sentence thesis
- core question
- global argument map
- chapter value grading
- topic/theme clusters
- concept index
- evidence index

Chapter value levels:

- `must-read`: generate detail page.
- `useful`: summarize and include in Book Home.
- `index-only`: keep source range and chapter role only.
- `skip`: show only if needed in chapter matrix.

## 5. Subagent Policy

Use subagents by topic group, not one agent for the whole book and not one agent per tiny chapter.

Good grouping:

- one subagent for one major theme and its related chapters
- one subagent for research/evidence extraction across selected chapters
- one subagent for high-value chapter detail extraction

Each subagent must output JSON-compatible data only. It must not redesign the page.

## 6. High-Value Chapter Deep Read

For each `must-read` chapter, extract:

- role cards
- overview cards
- argument chain
- frameworks
- cases
- research timeline
- decision rules
- evidence drawer entries

Every card or node must reference evidence by `sourceRef` or `evidenceRefs`.

## 7. Render

Use fixed templates from `.book-analyst/page-templates/` or the skill assets:

- `library-empty.html`
- `book-home-empty.html`
- `chapter-page-empty.html`

Fill data from:

- `analysis/book.json`
- `analysis/themes.json`
- `analysis/chapters/index.json`
- `analysis/chapters/chXX.json`
- `analysis/evidence/index.json`
- `analysis/concepts/index.json`

After the AI Agent fills JSON, render:

```bash
python skill/book-analyst/scripts/render_project.py --config .book-analyst/config.json --book-id <book-id>
```

The renderer writes:

```text
<webOutputRoot>/<book-id>/index.html
<webOutputRoot>/<book-id>/chapters/*.html
```

If the service is already running, rerendered HTML is visible after browser refresh. Restart is not required.

## 7.5 Serve

Start the static display service:

```bash
python skill/book-analyst/scripts/start_service.py --config .book-analyst/config.json --port 8765
```

The service reads files from `webOutputRoot`. When JSON changes, rerun the renderer and refresh the browser.

## 7.6 Generate a Book Knowledge Skill

After analysis is stable, optionally generate a reusable skill from the book's concepts and evidence:

```bash
python skill/book-analyst/scripts/generate_book_skill.py analysis/<book-id> --output-root generated-skills
```

The generated skill is a thinking aid. It must not pretend to contain the full source book.

## 8. Validate

Before handoff:

- run `scripts/validate_project.py`
- check source refs resolve
- check no empty modules render
- check all generated HTML opens
- check chapter source chips open `EvidenceDrawer`
- check navigation: Library -> Book Home -> Chapter Page -> Book Home and Home icon -> Library

## 9. Phase 4 Personal Reflection

Only after user reading or explicit memory context, generate:

- user reflections
- AI synthesis
- permanent note candidates
- Obsidian/database backlinks

Do not put personal claims into Phase 1-3 pages.
