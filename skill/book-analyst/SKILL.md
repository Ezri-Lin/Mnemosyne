---
name: book-analyst
description: Analyze books with an AI Agent methodology and generate a reusable visual reading system. Use when the user wants to configure a book library, install fixed Library/Book Home/Chapter Page templates, parse books into structured JSON/Markdown, select high-value chapters, generate static HTML reading-navigation pages, or run Mnemosyne as the display layer.
---

# Book Analyst

Use this skill to turn a book into a fixed, visual reading-navigation artifact:

```text
source book -> structured analysis JSON/Markdown -> static Library / Book Home / Chapter Page HTML
```

Do not redesign the front end for each book. Install the bundled empty templates, fill the data contracts, and render the same component system for every book.

## Resource Map

- For the complete generation workflow, read `references/workflow.md`.
- For fixed page slots and installed templates, read `references/template-contract.md`.
- For JSON fields and source trace rules, read `references/schema-guide.md`.
- For concrete HTML component patterns, read `references/html-patterns.md` and `templates/components.md`.
- For the theme token system, use `templates/themes/warm-paper.css`.
- For installable empty page shells, use `assets/page-templates/`.
- For empty JSON skeletons, use `assets/data-skeletons/`.

## First Run

If the project has no `.book-analyst/config.json`, initialize it:

```bash
python skill/book-analyst/scripts/init_project.py --project-root .
```

The initializer must ask or accept paths for:

- project root
- book source directory
- analysis output directory
- web output directory
- notes output directory
- knowledge output directory
- metadata store
- language, theme, and density

It also installs the three empty page templates and JSON skeletons into `.book-analyst/`.

## Standard Workflow

1. Confirm or create `.book-analyst/config.json`.
2. Locate or upload the source book.
3. Extract text and metadata.
4. Build a chapter index without reading the entire book into one context.
5. Generate God's-eye view, chapter value grading, themes, concepts, and evidence.
6. Deep-read only high-value chapters.
7. Fill `analysis/*.json` using the schemas.
8. Render `web/index.html` and `web/chapters/*.html` from fixed templates.
9. Validate source refs, missing modules, and HTML interactions.
10. Start or refresh Mnemosyne only as the display layer.

Useful commands:

```bash
# Install config, empty templates, and empty JSON skeletons.
python skill/book-analyst/scripts/init_project.py --project-root .

# Prepare one source book: copy source, extract text, split chapters.
python skill/book-analyst/scripts/prepare_book.py path/to/book.epub --config .book-analyst/config.json

# One-shot deterministic entry. It initializes if needed, then prepares the book.
python skill/book-analyst/scripts/run_flow.py --project-root . --source path/to/book.epub

# After AI fills analysis/<book-id>/*.json, render HTML.
python skill/book-analyst/scripts/render_project.py --config .book-analyst/config.json --book-id <book-id>

# Serve generated HTML. Refresh browser after rerendering; no restart needed.
python skill/book-analyst/scripts/start_service.py --config .book-analyst/config.json --port 8765

# Optional: turn extracted book knowledge into a reusable knowledge skill.
python skill/book-analyst/scripts/generate_book_skill.py analysis/<book-id> --output-root generated-skills
```

## Non-Negotiable Rules

- Do not invent book tags, reading modes, evidence, quotes, or user-personal value.
- Do not put full analysis data in the SQL metadata store.
- Keep analysis content in `analysis/`, notes in `notes/`, and HTML in `web/`.
- Every author claim, case, research item, quote, and major AI interpretation needs a `sourceRef`.
- Compact cards may summarize, but original evidence must remain accessible through `EvidenceDrawer`.
- Empty modules do not render. Do not leave large blank panels.
- Phase 1-3 are book analysis. Personal relevance belongs to Phase 4 or explicit user memory.

## Validate

Run the project validator before handing off:

```bash
python skill/book-analyst/scripts/validate_project.py --config .book-analyst/config.json
```

Use browser or Playwright checks after rendering final HTML.
